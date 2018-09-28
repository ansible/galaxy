import { Component, Input, OnInit } from '@angular/core';

@Component({
    selector: 'app-quality-details',
    templateUrl: './quality-details.component.html',
    styleUrls: ['./quality-details.component.less'],
})
export class QualityDetailsComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'QualityDetailsComponent';

    constructor() {}

    @Input()
    content: any;
    codeTasks: {};
    rulesViolated: any;
    totalViolations = 0;

    ngOnInit() {
        this.codeTasks = [];

        console.log(this.content);

        if (this.content.metadata_score === null) {
            this.content.metadata_score = 'NA';
        }

        if (this.content.compatibility_score === null) {
            this.content.compatibility_score = 'NA';
        }

        for (const el of this.content.summary_fields.task_messages) {
            if (el.is_linter_rule_violation && el.rule_severity > 0) {
                this.totalViolations += 1;
                el.severityIcon = this.getWarningClass(el.rule_severity);
                el.severityText = this.getWarningText(el.rule_severity);
                if (this.codeTasks[el.linter_rule_id]) {
                    this.codeTasks[el.linter_rule_id].violations_count += 1;
                } else {
                    el.violations_count = 1;
                    this.codeTasks[el.linter_rule_id] = el;
                }
            }
        }

        this.rulesViolated = Object.keys(this.codeTasks);

        console.log(this.codeTasks);
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
