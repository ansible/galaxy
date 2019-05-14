import * as React from 'react';

import { Repository } from '../../../resources/repositories/repository';
import { RepositoryService } from '../../../resources/repositories/repository.service';
import { RepositoryImportService } from '../../../resources/repository-imports/repository-import.service';

import { Injector } from '@angular/core';

import { BsModalService } from 'ngx-bootstrap';

import { Namespace } from '../../../resources/namespaces/namespace';

import * as moment from 'moment';

import { RepoListItem } from '../../components/my-content/repo-list-item';

import { ListView } from 'patternfly-react';

interface IProps {
    injector: Injector;
    namespace: Namespace;
    items: Repository[];

    setToLoading: (item: Repository) => void;
    refreshContent: () => void;
    setPolling: (isPolling: boolean) => void;
}

export class RepoDetail extends React.Component<IProps, {}> {
    repositoryService: RepositoryService;
    repositoryImportService: RepositoryImportService;
    modalService: BsModalService;

    constructor(props) {
        super(props);

        const { injector } = this.props;

        this.repositoryService = injector.get(RepositoryService);
        this.repositoryImportService = injector.get(RepositoryImportService);
        this.modalService = injector.get(BsModalService);
    }

    componentDidMount() {
        this.modalService.onHidden.subscribe(_ => {
            this.props.refreshContent();
        });
    }

    render() {
        const repos = this.mapRepos(this.props.items);
        return (
            <ListView>
                <div className='type-heading'>
                    Repositories <div className='counter'>{repos.length}</div>
                </div>

                {repos.map(repo => {
                    return (
                        <RepoListItem
                            namespace={this.props.namespace}
                            key={repo.id}
                            repo={repo}
                            handleAction={(event, r) =>
                                this.handleItemAction(event, r)
                            }
                        />
                    );
                })}
            </ListView>
        );
    }

    private handleItemAction(event, repo): void {
        if (repo) {
            switch (event) {
                case 'import':
                    this.importRepository(repo);
                    break;
                case 'delete':
                    this.deleteRepository(repo);
                    break;
                case 'deprecate':
                    this.deprecate(true, repo);
                    break;
                case 'undeprecate':
                    this.deprecate(false, repo);
                    break;
            }
        }
    }

    private deprecate(isDeprecated: boolean, repo: Repository): void {
        this.props.setToLoading(repo);
        repo.deprecated = isDeprecated;

        this.repositoryService.save(repo).subscribe(() => {
            this.props.refreshContent();
        });
    }

    private importRepository(repository: Repository) {
        // Start an import
        this.props.setPolling(true);
        this.props.setToLoading(repository);

        this.repositoryImportService
            .save({ repository_id: repository.id })
            .subscribe(response => {
                this.props.refreshContent();
            });
    }

    private deleteRepository(repository: Repository) {
        this.props.setToLoading(repository);

        this.repositoryService
            .destroy(repository)
            .subscribe(_ => this.props.refreshContent());
    }

    private mapRepos(repositories: Repository[]) {
        // Generate a new list of repos
        const updatedList: Repository[] = [];

        // Only poll imports if there are pending imports
        this.props.setPolling(false);
        repositories.forEach(repo => {
            if (
                repo.summary_fields.latest_import.state === 'PENDING' ||
                repo.summary_fields.latest_import.state === 'RUNNING'
            ) {
                this.props.setPolling(true);
            }

            repo = this.prepareRepository(repo);
            updatedList.push(repo);
        });

        return updatedList;
    }

    private prepareRepository(item: Repository): Repository {
        item['expanded'] = false;
        item['latest_import'] = {};
        item['detail_url'] = this.getDetailUrl(item);
        item['iconClass'] = this.getIconClass(item.format);
        if (item.summary_fields.latest_import) {
            item['latest_import'] = item.summary_fields.latest_import;
            if (item['latest_import']['finished']) {
                item['latest_import']['as_of_dt'] = moment(
                    item['latest_import']['finished'],
                ).fromNow();
            } else {
                item['latest_import']['as_of_dt'] = moment(
                    item['latest_import']['modified'],
                ).fromNow();
            }
        }

        return item;
    }

    private getDetailUrl(item: Repository) {
        return `/${item.summary_fields['namespace']['name']}/${item.name}`;
    }

    private getIconClass(repository_format: string) {
        let result = 'pficon-repository list-pf-icon list-pf-icon-small';
        switch (repository_format) {
            case 'apb':
                result = 'pficon-bundle list-pf-icon list-pf-icon-small';
                break;
            case 'role':
                result = 'fa fa-gear list-pf-icon list-pf-icon-small';
                break;
        }
        return result;
    }
}
