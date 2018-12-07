import { Component, OnInit, Input } from '@angular/core';

import { ContentService } from '../../../../../resources/content/content.service';
import { Content } from '../../../../../resources/content/content';

import {
    ContentTypesIconClasses,
    ContentTypesChoices,
} from '../../../../../enums/content-types.enum';

import { PluginTypes } from '../../../../../enums/plugin-types.enum';

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
    warningsLoading = true;

    community: any;
    quality: any;

    ngOnInit() {
        this.quality = this.getScore(this.repo.quality_score);
        this.community = this.getScore(this.repo.community_score);
        this.repo.summary_fields.content_objects.forEach(cont => {
            if (PluginTypes[cont.content_type]) {
                cont['icon_class'] = ContentTypesIconClasses.plugin;
                cont['type_text'] = PluginTypes[cont.content_type];
            } else {
                cont['icon_class'] = ContentTypesIconClasses[cont.content_type];
                cont['type_text'] = ContentTypesChoices[cont.content_type];
            }
        });

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

                this.warningsLoading = false;
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

    getScore(score) {
        if (score !== null) {
            return Math.round(score * 10) / 10;
        } else {
            return 'NA';
        }
    }
}
