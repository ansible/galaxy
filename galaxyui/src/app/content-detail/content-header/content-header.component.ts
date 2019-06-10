import { Component, Input, OnInit } from '@angular/core';

import { Router } from '@angular/router';

import { Content } from '../../resources/content/content';
import { Namespace } from '../../resources/namespaces/namespace';
import { Repository } from '../../resources/repositories/repository';
import { CollectionDetail } from '../../resources/collections/collection';

import { AuthService } from '../../auth/auth.service';
import { UserPreferences } from '../../resources/preferences/user-preferences';
import { PreferencesService } from '../../resources/preferences/preferences.service';

import {
    RepoFormats,
    RepoFormatsIconClasses,
    RepoFormatsTooltips,
} from '../../enums/repo-types.enum';

class HeaderData {
    repoType: RepoFormats;
    name: string;
    description: string;
    iconClass: string;
    tooltip: string;
    downloadCount: number;
    namespace: string;
    avatarUrl: string;
    issueTrackerUrl: string;
    scmUrl: string;
    scmIconClass: string;
    scmName: string;
    formatType: string;
    deprecated: boolean;
    score: any;
    travis_build_url: string;
    travis_status_url: string;
    follow_type: string;
    content_id: number;
    website: string;
    documentationLink: string;
}

export class RepoChangeEvent {
    repoType: RepoFormats;
    mainContent: Content;
}

@Component({
    selector: 'app-content-header',
    templateUrl: './content-header.component.html',
    styleUrls: ['./content-header.component.less'],
})
export class ContentHeaderComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'ContentHeaderComponent';

    constructor(
        private authService: AuthService,
        private preferencesService: PreferencesService,
        private router: Router,
    ) {}

    @Input()
    collection?: CollectionDetail;
    @Input()
    repository?: Repository;
    @Input()
    namespace?: Namespace;

    mainContent: Content = {} as Content;
    headerData: HeaderData;
    RepoFormats: typeof RepoFormats = RepoFormats;
    isFollower = false;
    followerClass = 'fa fa-user-plus';

    preferences: UserPreferences = null;

    ngOnInit() {
        if (this.collection) {
            this.mapCollection();
        } else if (this.repository) {
            this.mapRepository();
        }

        this.authService.me().subscribe(me => {
            if (me.authenticated) {
                this.preferencesService.get().subscribe(result => {
                    this.preferences = result;
                    this.setFollower();
                });
            }
        });
    }

    followCollection() {
        this.followerClass = 'fa fa-spin fa-spinner';

        if (this.isFollower) {
            const index = this.preferences[this.headerData.follow_type].indexOf(
                this.headerData.content_id,
            );
            this.preferences[this.headerData.follow_type].splice(index, 1);
        } else {
            this.preferences[this.headerData.follow_type].push(
                this.headerData.content_id,
            );
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
            this.preferences[this.headerData.follow_type].find(
                x => x === this.headerData.content_id,
            ) !== undefined
        ) {
            this.isFollower = true;
            this.followerClass = 'fa fa-user-times';
        } else {
            this.isFollower = false;
            this.followerClass = 'fa fa-user-plus';
        }
    }

    private mapCollection() {
        this.headerData = {
            namespace: this.collection.namespace.name,
            avatarUrl:
                this.collection.namespace.avatar_url || '/assets/avatar.png',
            iconClass: 'pficon-repository',
            tooltip: 'Collection',
            name: this.collection.name,
            description:
                this.collection.latest_version.metadata.description || '',
            downloadCount: this.collection.download_count,
            formatType: 'Collection',
            deprecated: this.collection.deprecated,
            score: {
                community_survey_count: this.collection.community_survey_count,
                community_score: this.collection.community_score,
                quality_score: this.collection.latest_version.quality_score,
            },
            follow_type: 'collections_followed',
            content_id: this.collection.id,
            scmUrl: this.collection.latest_version.metadata.repository,
            issueTrackerUrl: this.collection.latest_version.metadata.issues,
            scmIconClass: 'pficon-repository',
            documentationLink: this.collection.latest_version.metadata
                .documentation,
            website: this.collection.latest_version.metadata.homepage,
        } as HeaderData;
    }

    private mapRepository() {
        let description;
        // description for legacy roles
        if (
            !this.repository.description &&
            this.repository.summary_fields.content_objects.length === 1
        ) {
            description = this.repository.summary_fields.content_objects[0]
                .description;
        } else {
            description = this.repository.description;
        }

        this.headerData = {
            formatType: 'Role',
            repoType: RepoFormats[this.repository.format],
            iconClass: RepoFormatsIconClasses[this.repository.format],
            tooltip: RepoFormatsTooltips[this.repository.format],
            name: this.repository.name,
            description: description,
            namespace: this.repository.summary_fields.namespace['name'],
            avatarUrl: this.namespace.avatar_url || '/assets/avatar.png',
            downloadCount: this.repository.download_count,
            issueTrackerUrl: this.repository.issue_tracker_url,
            scmUrl: this.repository.external_url,
            scmName: this.repository.summary_fields.provider['name'],
            scmIconClass: 'fa fa-github',
            deprecated: this.repository.deprecated,
            score: this.repository,
            travis_build_url: this.repository.travis_build_url,
            travis_status_url: this.repository.travis_status_url,
            follow_type: 'repositories_followed',
            content_id: this.repository.id,
        } as HeaderData;
    }
}
