import {
    Component,
    OnInit
} from '@angular/core';

import {
    ActivatedRoute,
    Router
} from '@angular/router';

import * as moment          from 'moment';

import { Observable }       from 'rxjs/Observable';
import { forkJoin }         from 'rxjs/observable/forkJoin';

import { EmptyStateConfig } from 'patternfly-ng/empty-state/empty-state-config';

import {
    Action,
    ActionConfig
} from 'patternfly-ng/action';

import { ContentTypes }     from '../enums/content-types.enum';
import { RepoFormats }      from '../enums/repo-types.enum';
import { ViewTypes }        from '../enums/view-types.enum';
import { Content }          from '../resources/content/content';
import { Namespace }        from '../resources/namespaces/namespace';
import { PagedResponse }    from '../resources/paged-response';
import { Repository }       from '../resources/repositories/repository';
import { RepoChangeEvent }  from './repository/repository.component';

import { ContentService }   from '../resources/content/content.service';

class ContentTypeCounts {
    apb: number;
    module: number;
    moduleUtils: number;
    plugin: number;
    role: number;
}

@Component({
    selector: 'app-content-detail',
    templateUrl: './content-detail.component.html',
    styleUrls: ['./content-detail.component.less']
})
export class ContentDetailComponent implements OnInit {

    constructor(
        private router: Router,
        private route: ActivatedRoute,
        private contentService: ContentService
    ) {}

    pageTitle = '';
    content: Content[];
    repository: Repository;
    namespace: Namespace;
    showEmptyState = false;
    actionConfig: ActionConfig;
    emptyStateConfig: EmptyStateConfig;
    selectedContent: Content;
    pageLoading = true;

    ViewTypes: typeof ViewTypes = ViewTypes;
    RepoFormats: typeof RepoFormats = RepoFormats;

    repoType: RepoFormats;
    repoContent: Content;
    hasReadme = false;
    hasMetadata = false;
    metadataFilename = '';
    showingView: string = ViewTypes.detail;  // Control what's displayed on lower half of page
    metadata: object;

    contentCounts: ContentTypeCounts = {
        apb: 0,
        module: 0,
        moduleUtils: 0,
        plugin: 0,
        role: 0
    } as ContentTypeCounts;

    ngOnInit() {
        this.actionConfig = {
            primaryActions: [{
                id: 'search',
                title: 'Search',
                tooltip: 'View the search page'
            }]
        } as ActionConfig;

        this.emptyStateConfig = {
            actions: this.actionConfig,
            iconStyleClass: 'fa fa-frown-o',
            info: 'Well this is embarrassing. The content you requested could not be found. ' +
            'It may not exist in the Galaxy search index. Click the Search button below, ' +
            'to search our index.',
            title: 'Content Not Found'
        } as EmptyStateConfig;

        this.route.params.subscribe(params => {
            this.route.data.subscribe((data) => {
                this.repository = data['repository'];
                this.namespace = data['namespace'];
                this.content = data['content'];

                if (this.repository) {
                    this.repoType = RepoFormats[this.repository.format];
                }

                const req_content_name = params['content_name'];

                if (req_content_name && data['content'] && data['content'].length) {
                    this.selectedContent = this.findSelectedContent(req_content_name);
                }
                if (!this.repository || !this.content ||
                    (this.repository.format === RepoFormats.multi &&
                    req_content_name && !this.selectedContent)) {
                    // Requested content from a multicontent repo not found || No content found
                    this.showEmptyState = true;
                    this.pageTitle = '<i class="fa fa-frown-o"></i> Content Not Found';
                    this.pageLoading = false;
                } else {

                    // Append author type to breadcrumb
                    if (this.namespace.is_vendor) {
                        this.pageTitle = `<i class="fa fa-star"></i> Vendors;/vendors;`;
                    } else {
                        this.pageTitle = `<i class="fa fa-users"></i> Community Authors;/community;`;
                    }

                    // Append author namespace and repository name to breadcrumb
                    this.pageTitle += `${this.namespace.name};/${this.namespace.name};${params['repository']};`;

                    // If content is specified, append it to the breadcrumb
                    if (this.selectedContent) {
                        this.pageTitle += `/${this.namespace.name}/${params['repository']};${req_content_name}`;
                    }
                    this.repository.last_import = 'NA';
                    this.repository.last_commit = 'NA';
                    if (this.repository.summary_fields['latest_import'] &&
                        this.repository.summary_fields['latest_import']['finished']) {
                        this.repository.last_import =
                            moment(this.repository.summary_fields['latest_import']['finished']).fromNow();
                    }

                    if (this.repository.commit_created) {
                        this.repository.last_commit =
                            moment(this.repository.commit_created).fromNow();
                    }
                    if (this.content && this.content.length) {
                        this.repoContent = this.content[0];
                        this.fetchContentDetail(this.repoContent.id);
                    } else {
                        // Repo has no child Content Objects
                        this.pageLoading = false;
                        this.showEmptyState = true;
                    }
                }
            });
        });
    }

    toggleView(view: string) {
        this.showingView = ViewTypes[view];
    }

    handleActionClicked($event: Action) {
        this.router.navigate(['/search']);
    }

    // private

    private findSelectedContent(name: String): Content {
        // Find matching content by name
        let result: Content;
        if (!name) {
            return result;
        }
        this.content.forEach((item: Content) => {
            if (item.name === name) {
                result = JSON.parse(JSON.stringify(item));
            }
        });
        return result;
    }

    private fetchContentDetail(id: number) {
        this.contentService.get(id).subscribe(result => {
            this.repoContent = JSON.parse(JSON.stringify(result));
            this.hasMetadata = false;
            this.metadataFilename = '';
            this.metadata = null;
            this.hasReadme = false;
            if (this.repoContent.content_type === RepoFormats.role) {
                if (this.repoContent.metadata['container_meta']) {
                    this.hasMetadata = true;
                    this.metadataFilename = 'container.yml';
                    this.metadata = this.repoContent.metadata['container_meta'];
                }
                this.hasReadme = (this.repoContent.readme_html) ? true : false;
            }
            if (this.repoContent.content_type === RepoFormats.apb) {
                if (this.repoContent.metadata['apb_metadata']) {
                    this.hasMetadata = true;
                    this.metadataFilename = 'apb.yml';
                    this.metadata = this.repoContent.metadata['apb_metadata'];
                }
                this.hasReadme = (this.repoContent.readme_html) ? true : false;
            }
            if (this.repository.format === RepoFormats.multi) {
                if (this.repository.readme_html) {
                    this.hasReadme = true;
                    this.repoContent.readme_html = this.repository.readme_html;
                }
            }
            // Make it easier to access related data
            ['platforms', 'versions', 'cloud_platforms', 'dependencies'].forEach(key => {
                this.repoContent[key] = this.repoContent.summary_fields[key];
                let hasKey = 'has' + key[0].toUpperCase() + key.substring(1);
                hasKey = hasKey.replace(/\_(\w)/, this.toCamel);
                this.repoContent[hasKey] = (this.repoContent[key] && this.repoContent[key].length) ? true : false;
            });
            if (this.repository.format === RepoFormats.multi) {
                this.getContentTypeCounts();
            } else {
                this.pageLoading = false;
            }
        });
    }

    private toCamel(match: string, p1: string, offset: number, value: string): string {
        return p1.toUpperCase();
    }

    private getContentTypeCounts() {
        const queries: Array<Observable<PagedResponse>> = [];
        for (const content_type in ContentTypes) {
            if (ContentTypes.hasOwnProperty(content_type)) {
                if (ContentTypes[content_type] === 'plugin') {
                    queries.push(this.contentService.pagedQuery({
                        'repository__id': this.repository.id,
                        'content_type__name__icontains': ContentTypes[content_type]
                    }));
                } else {
                    queries.push(this.contentService.pagedQuery({
                        'repository__id': this.repository.id,
                        'content_type__name': ContentTypes[content_type]
                    }));
                }
            }
        }
        forkJoin(queries).subscribe((results: PagedResponse[]) => {
            results.forEach((result: PagedResponse) => {
                if (result['results'] && result['results'].length) {
                    const ct = result['results'][0]['content_type'];
                    if (ct.indexOf('plugin') > -1) {
                        this.contentCounts.plugin = result.count;
                    } else {
                        const ctKey = ct.replace(/\_(\w)/, this.toCamel);
                        this.contentCounts[ctKey] = result.count;
                    }
                }
            });
            this.pageLoading = false;
            if (this.selectedContent) {
                // For multi-content repo, set the detail view to the selected content item
                if (this.selectedContent.content_type === ContentTypes.module) {
                    this.showingView = ViewTypes.modules;
                } else if (this.selectedContent.content_type === ContentTypes.moduleUtils) {
                    this.showingView = ViewTypes.moduleUtils;
                } else if (this.selectedContent.content_type.indexOf('plugin') > -1) {
                    this.showingView = ViewTypes.plugins;
                } else if (this.selectedContent.content_type === ContentTypes.role) {
                    this.showingView = ViewTypes.roles;
                }
            }
        });
    }
}
