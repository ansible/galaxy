import { Component, Input, OnInit } from '@angular/core';

import { Content } from '../../resources/content/content';
import { Namespace } from '../../resources/namespaces/namespace';
import { Repository } from '../../resources/repositories/repository';

import { RepoFormats, RepoFormatsIconClasses, RepoFormatsTooltips } from '../../enums/repo-types.enum';

class RepositoryView {
    repoType: RepoFormats;
    name: string;
    displayName: string;
    description: string;
    iconClass: string;
    tooltip: string;
    watchersCount: number;
    stargazersCount: number;
    downloadCount: number;
    forksCount: number;
    namespace: string;
    avatarUrl: string;
    issueTrackerUrl: string;
    scmUrl: string;
    scmIconClass: string;
    scmName: string;
}

export class RepoChangeEvent {
    repoType: RepoFormats;
    mainContent: Content;
}

@Component({
    selector: 'content-detail-repo',
    templateUrl: './repository.component.html',
    styleUrls: ['./repository.component.less'],
})
export class RepositoryComponent implements OnInit {
    constructor() {}

    @Input()
    repository: Repository;
    @Input()
    namespace: Namespace;

    mainContent: Content = {} as Content;
    repositoryView: RepositoryView;
    RepoFormats: typeof RepoFormats = RepoFormats;

    ngOnInit() {
        this.setRepositoryView();
    }

    // private
    private setRepositoryView() {
        // Determine repoType: role, apb, multiconent
        this.repositoryView = {} as RepositoryView;
        this.repositoryView.repoType = RepoFormats[this.repository.format];
        this.repositoryView.iconClass = RepoFormatsIconClasses[this.repository.format];
        this.repositoryView.tooltip = RepoFormatsTooltips[this.repository.format];
        this.repositoryView.name = this.repository.name;

        // description for legacy roles
        if (!this.repository.description && this.repository.summary_fields.content_objects.length === 1) {
            this.repositoryView.description = this.repository.summary_fields.content_objects[0].description;
        } else {
            this.repositoryView.description = this.repository.description;
        }

        this.repositoryView.namespace = this.repository.summary_fields.namespace['name'];

        if (this.repository.summary_fields.namespace['is_vendor']) {
            // assuming vendor name in logo img
            this.repositoryView.displayName = '';
        } else {
            this.repositoryView.displayName = this.repository.summary_fields.namespace['name'];
        }

        if (!this.namespace.avatar_url) {
            // missing avatar_url
            this.repositoryView.displayName = this.repository.summary_fields.namespace['name'];
            this.repositoryView.avatarUrl = '/assets/avatar.png';
        } else {
            this.repositoryView.avatarUrl = this.namespace.avatar_url;
        }

        this.repositoryView.watchersCount = this.repository.watchers_count;
        this.repositoryView.stargazersCount = this.repository.stargazers_count;
        this.repositoryView.downloadCount = this.repository.download_count;
        this.repositoryView.forksCount = this.repository.forks_count;
        this.repositoryView.issueTrackerUrl = this.repository.issue_tracker_url;
        this.repositoryView.scmUrl = this.repository.external_url;
        this.repositoryView.scmName = this.repository.summary_fields.provider['name'];

        switch (this.repository.summary_fields.provider['name'].toLowerCase()) {
            case 'github':
                this.repositoryView.scmIconClass = 'fa fa-github';
                break;
        }
    }
}
