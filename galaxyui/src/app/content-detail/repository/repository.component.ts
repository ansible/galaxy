import { Component, Input, OnInit } from '@angular/core';

import { Router } from '@angular/router';

import { Content } from '../../resources/content/content';
import { Namespace } from '../../resources/namespaces/namespace';
import { Repository } from '../../resources/repositories/repository';

import { AuthService } from '../../auth/auth.service';
import { UserPreferences } from '../../resources/preferences/user-preferences';
import { PreferencesService } from '../../resources/preferences/preferences.service';

import {
    RepoFormats,
    RepoFormatsIconClasses,
    RepoFormatsTooltips,
} from '../../enums/repo-types.enum';

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
    // Used to track which component is being loaded
    componentName = 'RepositoryComponent';

    constructor(
        private authService: AuthService,
        private preferencesService: PreferencesService,
        private router: Router,
    ) {}

    @Input()
    repository: Repository;
    @Input()
    namespace: Namespace;

    mainContent: Content = {} as Content;
    repositoryView: RepositoryView;
    RepoFormats: typeof RepoFormats = RepoFormats;
    isFollower = false;
    followerClass = 'fa fa-user-plus';

    preferences: UserPreferences = null;

    ngOnInit() {
        this.authService.me().subscribe(me => {
            if (me.authenticated) {
                this.preferencesService.get().subscribe(result => {
                    this.preferences = result;
                    this.setFollower();
                });
            }
        });
        this.setRepositoryView();
    }

    followCollection() {
        this.followerClass = 'fa fa-spin fa-spinner';

        if (this.isFollower) {
            const index = this.preferences.repositories_followed.indexOf(
                this.repository.id,
            );
            this.preferences.repositories_followed.splice(index, 1);
        } else {
            this.preferences.repositories_followed.push(this.repository.id);
        }
        this.preferencesService.save(this.preferences).subscribe(result => {
            if (result !== null) {
                this.preferences = result;
                this.setFollower();
            }
        });
    }

    // private
    private setFollower() {
        if (
            this.preferences.repositories_followed.find(
                x => x === this.repository.id,
            ) !== undefined
        ) {
            this.isFollower = true;
            this.followerClass = 'fa fa-user-times';
        } else {
            this.isFollower = false;
            this.followerClass = 'fa fa-user-times';
        }
    }

    private setRepositoryView() {
        // Determine repoType: role, apb, multiconent
        this.repositoryView = {} as RepositoryView;
        this.repositoryView.repoType = RepoFormats[this.repository.format];
        this.repositoryView.iconClass =
            RepoFormatsIconClasses[this.repository.format];
        this.repositoryView.tooltip =
            RepoFormatsTooltips[this.repository.format];
        this.repositoryView.name = this.repository.name;

        // description for legacy roles
        if (
            !this.repository.description &&
            this.repository.summary_fields.content_objects.length === 1
        ) {
            this.repositoryView.description = this.repository.summary_fields.content_objects[0].description;
        } else {
            this.repositoryView.description = this.repository.description;
        }

        this.repositoryView.namespace = this.repository.summary_fields.namespace[
            'name'
        ];

        if (this.repository.summary_fields.namespace['is_vendor']) {
            // assuming vendor name in logo img
            this.repositoryView.displayName = '';
        } else {
            this.repositoryView.displayName = this.repository.summary_fields.namespace[
                'name'
            ];
        }

        if (!this.namespace.avatar_url) {
            // missing avatar_url
            this.repositoryView.displayName = this.repository.summary_fields.namespace[
                'name'
            ];
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
        this.repositoryView.scmName = this.repository.summary_fields.provider[
            'name'
        ];

        switch (this.repository.summary_fields.provider['name'].toLowerCase()) {
            case 'github':
                this.repositoryView.scmIconClass = 'fa fa-github';
                break;
        }
    }
}
