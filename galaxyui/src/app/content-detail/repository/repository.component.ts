import {
	Component,
    EventEmitter,
    Input,
    Output,
	OnInit
} from '@angular/core';

import { Repository }       from '../../resources/repositories/repository';
import { Content }          from '../../resources/content/content';
import { Namespace }        from '../../resources/namespaces/namespace';
import { ContentService }   from '../../resources/content/content.service';

import {
    RepoFormats,
    RepoFormatsTooltips,
    RepoFormatsIconClasses
} from '../../enums/repo-types.enum';

import * as moment          from 'moment';


class RepositoryView {
    repoType: RepoFormats;
    name: string;
    description: string;
    iconClass: string;
    tooltip: string;
    watchersCount: number;
    stargazersCount: number;
    downloadCount: number;
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
    styleUrls: ['./repository.component.less']
})
export class RepositoryComponent implements OnInit {

    constructor(
        private contentService: ContentService
    ) {}

    @Input() repository: Repository;
    @Input() namespace: Namespace;

    mainContent: Content = {} as Content;
    repositoryView: RepositoryView;
    RepoFormats: typeof RepoFormats = RepoFormats;

    ngOnInit() {
        this.setRepositoryView();
    }

    // private
    private setRepositoryView(){
        // Determine repoType: role, apb, multiconent
        this.repositoryView = {} as RepositoryView;
        this.repositoryView.repoType = RepoFormats[this.repository.format];
        this.repositoryView.iconClass = RepoFormatsIconClasses[this.repository.format];
        this.repositoryView.tooltip = RepoFormatsTooltips[this.repository.format];
        this.repositoryView.name = this.repository.name;
        this.repositoryView.description = this.repository.description;
        this.repositoryView.namespace = this.repository.summary_fields.namespace['name'];
        this.repositoryView.avatarUrl = this.namespace.avatar_url || '/assets/avatar.png';
        this.repositoryView.watchersCount = this.repository.watchers_count;
        this.repositoryView.stargazersCount = this.repository.stargazers_count;
        this.repositoryView.downloadCount = 0;
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
