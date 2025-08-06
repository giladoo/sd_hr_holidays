/** @odoo-module **/
import { Component } from "@odoo/owl"

export class TextBox extends Component {
    static template = "holidays_text_box_template";
    static props = { name: String, onClick: Function, value: Number, };
}

