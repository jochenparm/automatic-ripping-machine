"""
FADR route blueprint for history pages
Covers
- history [GET]
"""

from __future__ import annotations

import os

from flask import Blueprint, render_template, request, session
from flask_login import LoginManager, login_required  # noqa: F401

import fadr.config.config as cfg
import fadr.ui.utils as ui_utils
from fadr.models.job import Job
from fadr.ui import app, db

route_history = Blueprint('route_history', __name__,
                          template_folder='templates',
                          static_folder='../static')

# This attaches the fadrui_cfg globally to let the users use any bootswatch skin from cdn
fadrui_cfg = ui_utils.fadr_db_cfg()


@route_history.route('/history')
@login_required
def history():
    """
    Smaller much simpler output of previously run jobs

    """
    # regenerate the fadrui_cfg we don't want old settings
    fadrui_cfg = ui_utils.fadr_db_cfg()
    page = request.args.get('page', 1, type=int)
    if os.path.isfile(cfg.fadr_config['DBFILE']):
        # after roughly 175 entries firefox readermode will break
        # jobs = Job.query.filter_by().limit(175).all()
        jobs = Job.query.order_by(db.desc(Job.job_id)).paginate(page=page,
                                                                max_per_page=int(
                                                                    fadrui_cfg.database_limit),
                                                                error_out=False)
    else:
        app.logger.error('ERROR: /history database file doesnt exist')
        jobs = {}
    app.logger.debug(f"Date format - {cfg.fadr_config['DATE_FORMAT']}")

    session["page_title"] = "History"

    return render_template('history.html', jobs=jobs.items,
                           date_format=cfg.fadr_config['DATE_FORMAT'], pages=jobs)
