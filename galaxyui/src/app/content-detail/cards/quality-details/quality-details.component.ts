import { Component, Input, OnInit } from '@angular/core';

class WarningType {
    violationsCount: number;
    message: Set<string>;
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
    set content(content) {
        this.contentWarn = new Warning();
        this.metaWarn = new Warning();
        this.compatibilityWarn = new Warning();

        this.syntaxScore = this.convertScore(content.content_score);
        this.metadataScore = this.convertScore(content.metadata_score);

        for (const el of content.summary_fields.task_messages) {
            if (el.is_linter_rule_violation && el.rule_severity > 0) {
                if (el.score_type === 'content') {
                    this.addWarning(
                        this.contentWarn,
                        el.linter_rule_id,
                        el.rule_desc,
                        el.rule_severity,
                    );
                }
                if (el.score_type === 'metadata') {
                    this.addWarning(
                        this.metaWarn,
                        el.linter_rule_id,
                        el.rule_desc,
                        el.rule_severity,
                    );
                }
                if (el.score_type === 'compatibility') {
                    this.addWarning(
                        this.compatibilityWarn,
                        el.linter_rule_id,
                        el.rule_desc,
                        el.rule_severity,
                    );
                }
            }
        }
    }

    @Input()
    set collection(collection) {
        this.contentWarn = new Warning();
        this.metaWarn = new Warning();
        this.compatibilityWarn = new Warning();

        this.syntaxScore = '';
        this.metadataScore = '';

        for (const el of collection.lint_records) {
            if (el.severity > 0) {
                if (el.score_type === 'content') {
                    this.addWarning(
                        this.contentWarn,
                        `${el.type} ${el.code}`,
                        el.message,
                        el.severity,
                    );
                }
                if (el.score_type === 'metadata') {
                    this.addWarning(
                        this.metaWarn,
                        `${el.type} ${el.code}`,
                        el.message,
                        el.severity,
                    );
                }
                if (el.score_type === 'compatibility') {
                    this.addWarning(
                        this.compatibilityWarn,
                        `${el.type} ${el.code}`,
                        el.message,
                        el.severity,
                    );
                }
            }
        }
    }

    contentWarn: Warning;
    metaWarn: Warning;
    compatibilityWarn: Warning;

    syntaxScore: any;
    metadataScore: any;

    ngOnInit() {}

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

    private addWarning(warning, linter_rule_id, rule_desc, rule_severity) {
        warning.count += 1;
        if (warning.ruleDetails[linter_rule_id]) {
            warning.ruleDetails[linter_rule_id].violationsCount += 1;
            warning.ruleDetails[linter_rule_id].message.add(rule_desc);
        } else {
            const messages = new Set([rule_desc]);
            warning.rulesViolated.push(linter_rule_id);
            warning.ruleDetails[linter_rule_id] = {
                violationsCount: 1,
                message: messages,
                severityText: this.getWarningText(rule_severity),
                severityIcon: this.getWarningClass(rule_severity),
            } as WarningType;
        }
    }
}
