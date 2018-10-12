import { Component, Input, OnInit } from '@angular/core';

import { Router } from '@angular/router';

import { Content } from '../../resources/content/content';
import { Namespace } from '../../resources/namespaces/namespace';
import { Repository } from '../../resources/repositories/repository';

import { AuthService } from '../../auth/auth.service';
import { User } from '../../resources/users/user';
import { UserService } from '../../resources/users/user.service';

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
    // Used to track which component is being loaded
    componentName = 'RepositoryComponent';

    constructor(private authService: AuthService, private userService: UserService, private router: Router) {}

    @Input()
    repository: Repository;
    @Input()
    namespace: Namespace;

    mainContent: Content = {} as Content;
    repositoryView: RepositoryView;
    RepoFormats: typeof RepoFormats = RepoFormats;
    isFollower = false;

    me: User;

    ngOnInit() {
        this.authService.me().subscribe(me => {
            if (me.authenticated) {
                this.userService.get(me.id).subscribe(result => {
                    this.me = result;
                    this.setFollower();
                });
            } else {
                this.me = null;
            }
        });
        this.setRepositoryView();
    }

    followCollection() {
        if (this.isFollower) {
            const index = this.me.repositories_followed.indexOf(this.repository.id);
            this.me.repositories_followed.splice(index, 1);
        } else {
            this.me.repositories_followed.push(this.repository.id);
        }
        this.userService.save(this.me).subscribe(result => {
            if (result !== null) {
                this.me = result;
                this.setFollower();
            }
        });
    }

    // private
    private setFollower() {
        if (this.me.repositories_followed.find(x => x === this.repository.id) !== undefined) {
            this.isFollower = true;
        } else {
            this.isFollower = false;
        }
    }

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
