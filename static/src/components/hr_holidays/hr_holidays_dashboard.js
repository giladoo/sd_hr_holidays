/** @odoo-module **/

import { registry } from "@web/core/registry"
import { Component, useState, useRef, onMounted, onWillStart, onWillUnmount, useChildSubEnv } from '@odoo/owl';
import { _t } from "@web/core/l10n/translation";
import { download } from "@web/core/network/download";
import { browser } from "@web/core/browser/browser";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
const { DateTime } = luxon;
import { formatDate, formatDateTime } from "@web/core/l10n/dates";
//import { ChartBox} from "./chart_box/chart_box"
import { TextBox} from "./text_box/text_box"

const COL_3 = ' col-12 col-md-6 col-lg-3 '
const COL_4 = ' col-12 col-md-6 col-lg-4 '
const COL_6 = ' col-12 col-lg-6 '

export class SdHrHolidaysDashboard extends Component {
    static template = "holidays_dashboard_template";
    static components = {  TextBox };
    static props = ["*"];
    setup() {

        this.getData = this.getData.bind(this)
        this.onClick = this.onClick.bind(this);
        this.refresh_btn = this.refresh_btn.bind(this);

        this.state = useState({
            texts: {
                myRequests: {name: _t('Leave/Mission Request'), value: 0},
                myActions: {name: _t('Leave/Mission Approve'), value: 0},
                missionValidation: {name: _t('Mission Validation'), value: 0},
                myReports: {name: _t('Mission Reports'), value: 0},
                myApproves: {name: _t('Report Approves'), value: 0},
                notRegistered: {name: _t('Not Registered'), value: 0},
            },
        })
        this.orm = useService("orm")
        this.actionService = useService("action")
        onWillStart(async ()=>{
            await this.getData()
        })
        onMounted(async ()=>{
//            this.onTextClick([{total: ['', 0, 0]}])
//            let oActionManager = document.querySelector('.o_action_manager')
//            oActionManager && (oActionManager.style.overflowY = 'auto')
//            this.setPlotlyEvent()
        })
        onWillUnmount(()=>{
//            let oActionManager = document.querySelector('.o_action_manager')
//            oActionManager && (oActionManager.style.overflowY = '')
        })
//        console.log('this:', this, session)
    }
    async getData(){

        let getLeave = await this.orm.call('hr.leave', 'get_leaves', [false, ])
        getLeave = JSON.parse(getLeave)
//        readGroup(model, domain, fields, groupby, kwargs = {})

        console.log('getLeave:', getLeave)
        this.state.texts['myRequests'].value = getLeave.my_requests || 0
        this.state.texts['myActions'].value = getLeave.my_actions || 0
        this.state.texts['myReports'].value = getLeave.my_reports || 0
        this.state.texts['myApproves'].value = getLeave.my_approves || 0
        this.state.texts['notRegistered'].value = getLeave.not_registered || 0
        this.state.texts['missionValidation'].value = getLeave.mission_validation || 0

    }
    onClick(param){
        console.log('onClick', param)
        if (param == 'leave_request'){
            this.actionService.doAction("hr_holidays.hr_leave_action_new_request", {target: "new",})
        } else if (param == 'leave_approve'){
            this.actionService.doAction("hr_holidays.hr_leave_action_action_approve_department", {target: "new",})
        } else if (param == 'mission_report'){
            this.actionService.doAction("sd_hr_holidays.hr_leave_action_action_approve_department_2")
        } else if (param == 'report_approve'){
            this.actionService.doAction("sd_hr_holidays.hr_leave_action_action_approve_department_3")
        } else if (param == 'not_registered'){
            this.actionService.doAction("sd_hr_holidays.hr_leave_action_action_approve_department_4")
        } else if (param == 'mission_validation'){
            this.actionService.doAction("sd_hr_holidays.hr_leave_action_action_approve_department_5")
        }
//        this.actionService.doAction(
//            {
//                type: "ir.actions.act_window",
//                name: 'action_name',
//                res_model: 'hr.leave',
//                views: [[false, "list"],[false, "form"]],
////                view_mode: "list",
//                target: "new",
////                res_id: res_id,
////                domain: domain,
////                context: context,
//
//            })
    }
    async refresh_btn(){
      await this.getData()

    }

}

registry.category("actions").add("hr_holidays_dashboard", SdHrHolidaysDashboard);