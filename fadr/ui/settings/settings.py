"""
FADR route blueprint for settings pages
Covers
- settings [GET]
- save_settings [POST]
- save_ui_settings [POST]
- save_abcde_settings [POST]
- save_apprise_cfg [POST]
- systeminfo [POST]
- systemdrivescan [GET]
- update_fadr [POST]
- drive_eject [GET]
- drive_remove [GET]
- testapprise [GET]
"""
from __future__ import annotations

import importlib
import platform
import re
import subprocess
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session
from flask_login import (UserMixin, current_user, login_required,  # noqa: F401
                         login_user, logout_user)

import fadr.config.config as cfg
import fadr.ripper.utils as ripper_utils
import fadr.ui.utils as ui_utils
from fadr.models.job import Job
from fadr.models.system_drives import SystemDrives
from fadr.models.system_info import SystemInfo
from fadr.models.ui_settings import UISettings
from fadr.ui import app, db
from fadr.ui.forms import (AbcdeForm, SettingsForm, SystemInfoDrives,
                           UiSettingsForm)
from fadr.ui.settings import DriveUtils
from fadr.ui.settings.ServerUtil import ServerUtil

route_settings = Blueprint('route_settings', __name__,
                           template_folder='templates',
                           static_folder='../static')

# Page definitions
page_settings = "settings/settings.html"
redirect_settings = "/settings"


@route_settings.route('/settings')
@login_required
def settings():
    """
    Page - settings
    Method - GET
    Overview - allows the user to update the all configs of A.R.M without
    needing to open a text editor
    """
    global page_settings

    # stats for info page
    failed_rips = Job.query.filter_by(status="fail").count()
    total_rips = Job.query.filter_by().count()
    movies = Job.query.filter_by(video_type="movie").count()
    series = Job.query.filter_by(video_type="series").count()
    cds = Job.query.filter_by(disctype="music").count()

    # Get the current server time and timezone
    current_time = datetime.now()
    server_datetime = current_time.strftime(cfg.fadr_config['DATE_FORMAT'])
    server_timezone = current_time.astimezone().tzinfo
    [fadr_version_local, fadr_version_remote] = ui_utils.git_check_version()
    local_git_hash = ui_utils.get_git_revision_hash()

    stats = {'server_datetime': server_datetime,
             'server_timezone': server_timezone,
             'python_version': platform.python_version(),
             'fadr_version_local': fadr_version_local,
             'fadr_version_remote': fadr_version_remote,
             'git_commit': local_git_hash,
             'movies_ripped': movies,
             'series_ripped': series,
             'cds_ripped': cds,
             'no_failed_jobs': failed_rips,
             'total_rips': total_rips,
             'updated': ui_utils.git_check_updates(local_git_hash),
             'hw_support': check_hw_transcode_support()
             }

    # FADR UI config
    fadrui_cfg = ui_utils.fadr_db_cfg()

    # System details in class server
    server = SystemInfo.query.filter_by(id="1").first()
    serverutil = ServerUtil()

    # System details in class server
    fadr_path = cfg.fadr_config['TRANSCODE_PATH']
    media_path = cfg.fadr_config['COMPLETED_PATH']

    # System Drives (CD/DVD/Blueray drives)
    drives = DriveUtils.drives_check_status()
    form_drive = SystemInfoDrives(request.form)

    # Load up the comments.json, so we can comment the fadr.yaml
    comments = ui_utils.generate_comments()
    form = SettingsForm()

    session["page_title"] = "Settings"

    return render_template(page_settings,
                           settings=cfg.fadr_config,
                           ui_settings=fadrui_cfg,
                           stats=stats,
                           apprise_cfg=cfg.apprise_config,
                           form=form,
                           jsoncomments=comments,
                           abcde_cfg=cfg.abcde_config,
                           server=server,
                           serverutil=serverutil,
                           fadr_path=fadr_path,
                           media_path=media_path,
                           drives=drives,
                           form_drive=form_drive)


def check_hw_transcode_support():
    cmd = f"nice {cfg.fadr_config['HANDBRAKE_CLI']}"

    app.logger.debug(f"Sending command: {cmd}")
    hw_support_status = {
        "nvidia": False,
        "intel": False,
        "amd": False
    }
    try:
        hand_brake_output = subprocess.run(f"{cmd}", capture_output=True, shell=True, check=True)

        # NVENC
        if re.search(r'nvenc: version ([0-9\\.]+) is available', str(hand_brake_output.stderr)):
            app.logger.info("NVENC supported!")
            hw_support_status["nvidia"] = True
        # Intel QuickSync
        if re.search(r'qsv:\sis(.*?)available\son', str(hand_brake_output.stderr)):
            app.logger.info("Intel QuickSync supported!")
            hw_support_status["intel"] = True
        # AMD VCN
        if re.search(r'vcn:\sis(.*?)available\son', str(hand_brake_output.stderr)):
            app.logger.info("AMD VCN supported!")
            hw_support_status["amd"] = True
        app.logger.info("Handbrake call successful")
        # Dump the whole CompletedProcess object
        app.logger.debug(hand_brake_output)
    except subprocess.CalledProcessError as hb_error:
        err = f"Call to handbrake failed with code: {hb_error.returncode}({hb_error.output})"
        app.logger.error(err)
    return hw_support_status


@route_settings.route('/save_settings', methods=['POST'])
@login_required
def save_settings():
    """
    Page - save_settings
    Method - POST
    Overview - Save fadr ripper settings from post. Not a user page
    """
    # Load up the comments.json, so we can comment the fadr.yaml
    comments = ui_utils.generate_comments()
    success = False
    fadr_cfg = {}
    form = SettingsForm()
    if form.validate_on_submit():
        # Build the new fadr.yaml with updated values from the user
        fadr_cfg = ui_utils.build_fadr_cfg(request.form.to_dict(), comments)
        # Save updated fadr.yaml
        with open(cfg.fadr_config_path, "w") as settings_file:
            settings_file.write(fadr_cfg)
            settings_file.close()
        success = True
        importlib.reload(cfg)
        # Set the FADR Log level to the config
        app.logger.info(f"Setting log level to: {cfg.fadr_config['LOGLEVEL']}")
        app.logger.setLevel(cfg.fadr_config['LOGLEVEL'])

    # If we get to here there was no post data
    return {'success': success, 'settings': cfg.fadr_config, 'form': 'fadr ripper settings'}


@route_settings.route('/save_ui_settings', methods=['POST'])
@login_required
def save_ui_settings():
    """
    Page - save_ui_settings
    Method - POST
    Overview - Save 'UI Settings' page settings to database. Not a user page
    Notes - This function needs to trigger a restart of flask for
        debugging to update the values
    """
    form = UiSettingsForm()
    success = False
    fadr_ui_cfg = UISettings.query.get(1)
    if form.validate_on_submit():
        use_icons = (str(form.use_icons.data).strip().lower() == "true")
        save_remote_images = (str(form.save_remote_images.data).strip().lower() == "true")
        fadr_ui_cfg.index_refresh = format(form.index_refresh.data)
        fadr_ui_cfg.use_icons = use_icons
        fadr_ui_cfg.save_remote_images = save_remote_images
        fadr_ui_cfg.bootstrap_skin = format(form.bootstrap_skin.data)
        fadr_ui_cfg.language = format(form.language.data)
        fadr_ui_cfg.database_limit = format(form.database_limit.data)
        fadr_ui_cfg.notify_refresh = format(form.notify_refresh.data)
        db.session.commit()
        success = True
    # Masking the jinja update, otherwise an error is thrown
    # sqlalchemy.orm.exc.DetachedInstanceError: Instance <UISettings at 0x7f294c109fd0>
    # app.jinja_env.globals.update(fadrui_cfg=fadr_ui_cfg)
    return {'success': success, 'settings': str(fadr_ui_cfg), 'form': 'fadr ui settings'}


@route_settings.route('/save_abcde_settings', methods=['POST'])
@login_required
def save_abcde():
    """
    Page - save_abcde_settings
    Method - POST
    Overview - Save 'abcde Config' page settings to database. Not a user page
    """
    success = False
    abcde_cfg_str = ""
    form = AbcdeForm()
    if form.validate():
        app.logger.debug(f"routes.save_abcde: Saving new abcde.conf: {cfg.abcde_config_path}")
        abcde_cfg_str = str(form.abcdeConfig.data).strip()
        # Windows machines can put \r\n instead of \n newlines, which corrupts the config file
        clean_abcde_str = '\n'.join(abcde_cfg_str.splitlines())
        # Save updated abcde.conf
        with open(cfg.abcde_config_path, "w") as abcde_file:
            abcde_file.write(clean_abcde_str)
            abcde_file.close()
        success = True
        # Update the abcde config
        cfg.abcde_config = clean_abcde_str

    # If we get to here, there was no post-data
    return {'success': success, 'settings': clean_abcde_str, 'form': 'abcde config'}


@route_settings.route('/save_apprise_cfg', methods=['POST'])
@login_required
def save_apprise_cfg():
    """
    Page - save_apprise_cfg
    Method - POST
    Overview - Save 'Apprise Config' page settings to database. Not a user page
    """
    success = False
    # Since we can't be sure of any values, we can't validate it
    if request.method == 'POST':
        # Save updated apprise.yaml
        # Build the new fadr.yaml with updated values from the user
        apprise_cfg = ui_utils.build_apprise_cfg(request.form.to_dict())
        with open(cfg.apprise_config_path, "w") as settings_file:
            settings_file.write(apprise_cfg)
            settings_file.close()
        success = True
        importlib.reload(cfg)
    # If we get to here there was no post data
    return {'success': success, 'settings': cfg.apprise_config, 'form': 'Apprise config'}


@route_settings.route('/systeminfo', methods=['POST'])
@login_required
def server_info():
    """
    Page - systeminfo
    Method - POST
    Overview - Save 'System Info' page settings to database. Not a user page
    """
    global redirect_settings

    # System Drives (CD/DVD/Blueray drives)
    form_drive = SystemInfoDrives(request.form)
    if request.method == 'POST' and form_drive.validate():
        # Return for POST
        app.logger.debug(
            f"Drive id: {str(form_drive.id.data)} " +
            f"Updated name: [{str(form_drive.name.data)}] " +
            f"Updated description: [{str(form_drive.description.data)}]")
        drive = SystemDrives.query.filter_by(drive_id=form_drive.id.data).first()
        drive.name = str(form_drive.name.data).strip()
        drive.description = str(form_drive.description.data).strip()
        drive.drive_mode = str(form_drive.drive_mode.data).strip()
        db.session.commit()
        flash(f"Updated Drive {drive.mount} details", "success")
        # Return to systeminfo page (refresh page)
        return redirect(redirect_settings)
    else:
        flash("Error: Unable to update drive details", "error")
        # Return for GET
        return redirect(redirect_settings)


@route_settings.route('/systemdrivescan')
def system_drive_scan():
    """
    Page - systemdrivescan
    Method - GET
    Overview - Scan for the system drives and update the database.
    """
    global redirect_settings
    # Update to scan for changes to the ripper system
    new_count = DriveUtils.drives_update()
    flash(f"FADR found {new_count} new drives", "success")
    return redirect(redirect_settings)


@route_settings.route('/drive/eject/<eject_id>')
@login_required
def drive_eject(eject_id):
    """
    Server System - change state of CD/DVD/BluRay drive - toggle eject
    """
    global redirect_settings
    drive = SystemDrives.query.filter_by(drive_id=eject_id).first()
    drive.open_close()
    db.session.commit()
    return redirect(redirect_settings)


@route_settings.route('/drive/remove/<remove_id>')
@login_required
def drive_remove(remove_id):
    """
    Server System - remove a drive from the FADR UI
    """
    global redirect_settings
    try:
        app.logger.debug(f"Removing drive {remove_id}")
        drive = SystemDrives.query.filter_by(drive_id=remove_id).first()
        dev_path = drive.mount
        SystemDrives.query.filter_by(drive_id=remove_id).delete()
        db.session.commit()
        flash(f"Removed drive [{dev_path}] from FADR", "success")
    except Exception as e:
        app.logger.error(f"Drive removal encountered an error: {e}")
        flash("Drive unable to be removed, check logs for error", "error")
    return redirect(redirect_settings)


@route_settings.route('/drive/manual/<manual_id>')
@login_required
def drive_manual(manual_id):
    """
    Manually start a job on FADR
    """

    drive = SystemDrives.query.filter_by(drive_id=manual_id).first()
    dev_path = drive.mount.lstrip('/dev/')

    cmd = f"/opt/fadr/scripts/docker/docker_fadr_wrapper.sh {dev_path}"
    app.logger.debug(f"Running command[{cmd}]")

    # Manually start FADR if the udev rules are not working for some reason
    try:
        manual_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = manual_process.communicate()

        if manual_process.returncode != 0:
            raise subprocess.CalledProcessError(manual_process.returncode, cmd, output=stdout, stderr=stderr)

        message = f"Manually starting a job on Drive: '{drive.name}'"
        status = "success"
        app.logger.debug(stdout)

    except subprocess.CalledProcessError as e:
        message = f"Failed to start a job on Drive: '{drive.name}' See logs for info"
        status = "danger"
        app.logger.error(message)
        app.logger.error(f"error: {e}")
        app.logger.error(f"stdout: {e.output}")
        app.logger.error(f"stderr: {e.stderr}")

    flash(message, status)
    return redirect('/settings')


@route_settings.route('/testapprise')
def testapprise():
    """
    Page - testapprise
    Method - GET
    Overview - Send a test notification to Apprise.
    """
    global redirect_settings
    # Send a sample notification
    message = "This is a notification by the FADR-Notification Test!"
    if cfg.fadr_config["UI_BASE_URL"] and cfg.fadr_config["WEBSERVER_PORT"]:
        message = message + f" Server URL: http://{cfg.fadr_config['UI_BASE_URL']}:{cfg.fadr_config['WEBSERVER_PORT']}"
    ripper_utils.notify(None, "FADR notification", message)
    flash("Test notification sent ", "success")
    return redirect(redirect_settings)
