import { Component, Input, OnInit } from '@angular/core';

class WarningType {
    violationsCount: number;
    message: string;
    severityIcon: string;
    severityText: string;
}

class Warning {
    count: number;
    rulesViolated: string[];
    ruleDetails: {};

    constructor() {
        this.count = 0;
        this.rulesViolated = [];
        this.ruleDetails = {};
    }
}

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

    contentWarn: Warning;
    metaWarn: Warning;
    compatibilityWarn: Warning;

    ngOnInit() {
        this.contentWarn = new Warning();
        this.metaWarn = new Warning();
        this.compatibilityWarn = new Warning();

        this.content.content_score = this.convertScore(
            this.content.content_score,
        );
        this.content.metadata_score = this.convertScore(
            this.content.metadata_score,
        );
        this.content.compatibility_score = this.convertScore(
            this.content.compatibility_score,
        );

        for (const el of this.content.summary_fields.task_messages) {
            if (el.is_linter_rule_violation && el.rule_severity > 0) {
                if (el.score_type === 'content') {
                    this.addWarning(this.contentWarn, el);
                }
                if (el.score_type === 'metadata') {
                    this.addWarning(this.metaWarn, el);
                }
                if (el.score_type === 'compatibility') {
                    this.addWarning(this.compatibilityWarn, el);
                }
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

    private convertScore(score: number) {
        if (score === null) {
            return 'NA';
        }

        return Math.round(score * 10) / 10;
    }

    private addWarning(warning, task) {
        warning.count += 1;
        if (warning.ruleDetails[task.linter_rule_id]) {
            warning.ruleDetails[task.linter_rule_id].violationsCount += 1;
        } else {
            warning.rulesViolated.push(task.linter_rule_id);
            warning.ruleDetails[task.linter_rule_id] = {
                violationsCount: 1,
                message: task.rule_desc,
                severityText: this.getWarningText(task.rule_severity),
                severityIcon: this.getWarningClass(task.rule_severity),
            } as WarningType;
        }
    }
}
