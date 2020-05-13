# -*- coding: utf8 -*-

from flask import Blueprint, render_template

from libs.common import login_check

statistical_blue = Blueprint('statistical', __name__, template_folder='../../templates', static_folder='../../statices',
                             url_prefix='/statistical')


@statistical_blue.route('/planet_data_chart', methods=['get'])
@login_check
def planet_data_chart():
    return render_template('statistical/planet_data_chart.html')


@statistical_blue.route('/user_data_chart', methods=['get'])
@login_check
def user_data_chart():
    return render_template('statistical/user_data_chart.html')


@statistical_blue.route('/heat_data_chart', methods=['get'])
@login_check
def heat_data_chart():
    return render_template('statistical/heat_data_chart.html')


@statistical_blue.route('/red_data_chart', methods=['get'])
@login_check
def red_data_chart():
    return render_template('statistical/red_data_chart.html')


@statistical_blue.route('/user_list', methods=['get'])
@login_check
def user_list():
    return render_template('statistical/user_list.html')


@statistical_blue.route('/video_list', methods=['get'])
@login_check
def video_list():
    return render_template('statistical/video_list.html')


@statistical_blue.route('/home_ad_list', methods=['get'])
@login_check
def home_ad_list():
    return render_template('statistical/home_ad_list.html')


@statistical_blue.route('/banner_list', methods=['get'])
@login_check
def banner_list():
    return render_template('statistical/banner_list.html')


@statistical_blue.route('/lottery_list', methods=['get'])
@login_check
def lottery_list():
    return render_template('statistical/lottery_list.html')


@statistical_blue.route('/black_card_list', methods=['get'])
@login_check
def black_card_list():
    return render_template('statistical/black_card_list.html')


@statistical_blue.route('/taobao_list', methods=['get'])
@login_check
def taobao_list():
    return render_template('statistical/taobao_list.html')


@statistical_blue.route('/hungry_list', methods=['get'])
@login_check
def hungry_list():
    return render_template('statistical/hungry_list.html')


@statistical_blue.route('/user_analysis_list', methods=['get'])
@login_check
def user_analysis_list():
    return render_template('statistical/user_analysis_list.html')


@statistical_blue.route('/user_balance_list', methods=['get'])
@login_check
def user_balance_list():
    return render_template('statistical/user_balance_list.html')


@statistical_blue.route('/statistical_official_invite', methods=['get'])
@login_check
def statistical_official_invite():
    return render_template('statistical/statistical_official_invite.html')
