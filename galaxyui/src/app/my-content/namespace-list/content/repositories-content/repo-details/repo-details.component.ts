import { Component, OnInit, Input } from '@angular/core';

import { ContentService } from '../../../../../resources/content/content.service';
import { Content } from '../../../../../resources/content/content';

@Component({
    selector: 'app-repo-details',
    templateUrl: './repo-details.component.html',
    styleUrls: ['./repo-details.component.less'],
})
export class RepoDetailsComponent implements OnInit {
    constructor(private contentService: ContentService) {}

    @Input()
    repo;

    repoContent: Content[];
    warnings: any[] = [];

    ngOnInit() {
        this.contentService
            .query({ repository_id: this.repo.id, page_size: 1000 })
            .subscribe(response => {
                this.repoContent = response as Content[];

                for (const cont of this.repoContent) {
                    for (const task of cont.summary_fields['task_messages']) {
                        if (task.message_type === 'WARNING') {
                            task.warn_class = this.getWarningClass(
                                task.rule_severity,
                            );
                            this.warnings.push(task);
                        }
                    }
                }
            });
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
}
