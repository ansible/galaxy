import { Component, Input, OnInit } from '@angular/core';

@Component({
    selector: 'app-quality-details',
    templateUrl: './quality-details.component.html',
    styleUrls: ['./quality-details.component.less'],
})
export class QualityDetailsComponent implements OnInit {
    constructor() {}

    @Input()
    content: any;

    codeTasks: any;

    ngOnInit() {
        this.codeTasks = [];

        for (const el of this.content.summary_fields.task_messages) {
            if (el.is_linter_rule_violation && el.severity > 0) {
                el.severityIcon = this.getWarningClass(el.severity);
                el.severityText = this.getWarningText(el.severity);
                this.codeTasks.push(el);
            }
        }
    }

    getWarningClass(severity: number): string {
        if (severity >= 4) {
            return 'pficon-error-circle-o';
        } else if (severity <= 1) {
            return 'pficon-info';
        } else {
            return 'pficon-warning-triangle-o';
        }
    }

    getWarningText(severity: number): string {
        const text = 'Severity: ';
        if (severity === 1) {
            return text + 'Very Low';
        } else if (severity === 2) {
            return text + 'Low';
        } else if (severity === 3) {
            return text + 'Medium';
        } else if (severity === 4) {
            return text + 'High';
        } else if (severity === 5) {
            return text + 'Very High';
        }
    }
}
