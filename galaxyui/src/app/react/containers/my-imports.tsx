import * as React from 'react';
import { interval, Subscription } from 'rxjs';
import { cloneDeep } from 'lodash';

// Services
import { Injector } from '@angular/core';
import { Location } from '@angular/common';
import { ImportsService } from '../../resources/imports/imports.service';
import { AuthService } from '../../auth/auth.service';

// Types
import { ContentFormat } from '../../enums/format';
import { PulpStatus, ImportState } from '../../enums/import-state.enum';
import { ImportList, ImporterMessage } from '../../resources/imports/import';
import { Namespace } from '../../resources/namespaces/namespace';
import { ImportMetadata } from '../shared-types/my-imports';

// Components
import { ImportListComponent } from '../components/my-imports/import-list';
import { PageHeader } from '../components/page-header';
import { ImportConsoleComponent } from '../components/my-imports/import-console';

interface IProps {
    injector: Injector;
    namespaces: Namespace[];
    queryParams: any;
    selectedNamespace?: number;
    importList?: any;
}

interface IState {
    selectedNS: Namespace;
    queryParams: any;
    importList: ImportList[];
    selectedImport: ImportList;
    taskMessages: ImporterMessage[];
    followMessages: boolean;
    importMetadata: ImportMetadata;
    noImportsExist: boolean;
    resultsCount: number;
}

export class MyImportsPage extends React.Component<IProps, IState> {
    importsService: ImportsService;
    authService: AuthService;
    location: Location;
    polling: Subscription;

    constructor(props) {
        super(props);

        // The state of the page is mostly loaded by a series of API calls that
        // need to happen in a sequential order, so we'll initialize the state
        // as null and then load each piece as it comes in through the API.

        // This page basically requires three pieces of information:
        // - the tasks to display in the terminal, which we can't load until
        //   the list of imports is loaded
        // - the list of imports, which can't be loaded until the namespace is
        //   picked
        // - the namespace, which can't be loaded until the list of the user's
        //   namespaces is available

        this.state = {
            selectedNS: null,
            importList: null,
            selectedImport: null,
            taskMessages: null,
            followMessages: false,
            importMetadata: {} as ImportMetadata,
            noImportsExist: false,
            queryParams: this.props.queryParams,
            resultsCount: 0,
        };
    }

    componentDidMount() {
        this.importsService = this.props.injector.get(ImportsService);
        this.authService = this.props.injector.get(AuthService);
        this.location = this.props.injector.get(Location);

        this.polling = interval(2000).subscribe(() => {
            if (
                this.state.importMetadata.state === PulpStatus.running ||
                this.state.importMetadata.state === PulpStatus.waiting
            ) {
                this.poll();
            }
        });

        this.loadSelectedNS();
    }

    render() {
        return (
            <div className='my-imports-wrapper'>
                <PageHeader
                    headerTitle='My Imports'
                    headerIcon='fa fa-upload'
                />
                <div className='row'>
                    <div className='col-sm-4'>
                        <ImportListComponent
                            namespaces={this.props.namespaces}
                            selectedNS={this.state.selectedNS}
                            importList={this.state.importList}
                            selectedImport={this.state.selectedImport}
                            selectImport={x => this.selectImportDetail(x)}
                            selectNamespace={ns => this.selectedNamespace(ns)}
                            noImportsExist={this.state.noImportsExist}
                            queryParams={this.state.queryParams}
                            numberOfResults={this.state.resultsCount}
                            setQueryParams={x => this.SetQueryParams(x)}
                        />
                    </div>
                    <div className='col-sm-8'>
                        <ImportConsoleComponent
                            taskMessages={this.state.taskMessages}
                            followMessages={this.state.followMessages}
                            selectedImport={this.state.selectedImport}
                            importMetadata={this.state.importMetadata}
                            noImportsExist={this.state.noImportsExist}
                            toggleFollowMessages={() =>
                                this.toggleFollowMessages()
                            }
                        />
                    </div>
                </div>
            </div>
        );
    }

    setState(newState, callback?) {
        // Update the page's URL if the queryParams or namespace state changes
        super.setState(newState, callback);

        if (newState.queryParams || newState.selectedNS) {
            const params = newState.queryParams || this.state.queryParams;
            const ns = newState.selectedNS || this.state.selectedNS;

            let paramString = '';
            for (const key of Object.keys(params)) {
                paramString += key + '=' + params[key] + '&';
            }

            // Remove trailing '&'
            paramString = paramString.substring(0, paramString.length - 1);

            this.location.replaceState(`my-imports/${ns.id}`, paramString);
        }
    }

    componentWillUnmount() {
        if (this.polling) {
            this.polling.unsubscribe();
        }
    }

    private poll() {
        this.loadTaskMessages(() => {
            // Update the state of the selected import in the list if it's
            // different from the one loaded from the API. This makes it so
            if (
                this.state.selectedImport.state !==
                this.state.importMetadata.state
            ) {
                const importIndex = this.state.importList.findIndex(
                    x =>
                        x.id === this.state.selectedImport.id &&
                        x.type === this.state.selectedImport.type,
                );

                const imports = cloneDeep(this.state.importList);
                const selectedImport = cloneDeep(this.state.selectedImport);

                imports[importIndex].state = this.state.importMetadata.state;
                imports[
                    importIndex
                ].finished_at = this.state.importMetadata.finished_date;
                selectedImport.state = this.state.importMetadata.state;
                selectedImport.finished_at = this.state.importMetadata.finished_date;

                this.setState({
                    selectedImport: selectedImport,
                    importList: imports,
                });
            }
        });
    }

    private SetQueryParams(params) {
        this.setState(
            { queryParams: params, importList: null, noImportsExist: false },
            () => this.loadImportList(true),
        );
    }

    private toggleFollowMessages() {
        this.setState({ followMessages: !this.state.followMessages });
    }

    private loadSelectedNS() {
        if (this.props.selectedNamespace) {
            const selectedNS = this.props.namespaces.find(
                x => x.id === this.props.selectedNamespace,
            );

            this.setState({ selectedNS: selectedNS }, () =>
                this.loadImportList(),
            );
        } else {
            this.authService.me().subscribe(me => {
                // If no namespace is defined by the route, load whichever one
                // matches the user's username.
                let selectedNS = this.props.namespaces.find(
                    x => x.name === me.username,
                );

                // If no match is found, just use the first namespace in the
                // list
                if (selectedNS === undefined) {
                    selectedNS = this.props.namespaces[0];
                }

                this.setState({ selectedNS: selectedNS }, () =>
                    this.loadImportList(),
                );
            });
        }
    }

    private loadImportList(forceLoad = false) {
        // If the namespace has been pre loaded via URL params then it gets
        // passed to this component via props and we don't have to load it from
        // the API
        if (this.props.importList && !forceLoad) {
            this.setState(
                {
                    selectedImport: this.props.importList.results[0],
                    importList: this.props.importList.results,
                    resultsCount: this.props.importList.count,
                },
                () => this.loadTaskMessages(),
            );
        } else {
            this.importsService
                .get_import_list(
                    this.state.selectedNS.id,
                    this.state.queryParams,
                )
                .subscribe(importList => {
                    this.setState(
                        {
                            importList: importList.results,
                            selectedImport: importList.results[0],
                            resultsCount: importList.count,
                        },
                        () => this.loadTaskMessages(),
                    );
                });
        }
    }

    private loadTaskMessages(callback?: () => void) {
        if (!this.state.selectedImport) {
            this.setState({ noImportsExist: true });
        } else if (
            this.state.selectedImport.type === ContentFormat.collection
        ) {
            this.importsService
                .get_collection_import(this.state.selectedImport.id)
                .subscribe(result => {
                    this.setState(
                        {
                            noImportsExist: false,
                            taskMessages: result.messages,
                            importMetadata: {
                                version: result.version,
                                error: result.error
                                    ? result.error.description
                                    : null,
                                state: result.state,
                            } as ImportMetadata,
                        },
                        callback,
                    );
                });
        } else if (
            this.state.selectedImport.type === ContentFormat.repository
        ) {
            // Map repo import messages so that they look like collection
            // messages
            this.importsService
                .get_repo_import(this.state.selectedImport.id)
                .subscribe(result => {
                    this.setState(
                        {
                            taskMessages: result.summary_fields.task_messages.map(
                                el => {
                                    return {
                                        level: el.message_type,
                                        message: el.message_text,
                                        time: '',
                                    };
                                },
                            ),
                            importMetadata: {
                                state: this.mapStates(result.state),
                                branch: result.import_branch,
                                commit_message: result.commit_message,
                                travis_build_url: result.travis_build_url,
                                travis_status_url: result.travis_status_url,
                            } as ImportMetadata,
                        },
                        callback,
                    );
                });
        }
    }

    private mapStates(state) {
        switch (state) {
            case ImportState.pending:
                return PulpStatus.running;
            case ImportState.running:
                return PulpStatus.running;
            case ImportState.failed:
                return PulpStatus.failed;
            case ImportState.success:
                return PulpStatus.completed;
        }
    }

    private selectImportDetail(item: ImportList) {
        this.setState(
            {
                selectedImport: item,
                taskMessages: null,
                importMetadata: {} as ImportMetadata,
            },
            () => this.loadTaskMessages(),
        );
    }

    private selectedNamespace(nsID: number) {
        // For some reason the value passed back by the react component isn't
        // a number
        // tslint:disable-next-line:triple-equals
        const ns = this.props.namespaces.find(x => x.id == nsID);

        this.setState(
            {
                selectedNS: ns,
                importList: null,
                noImportsExist: false,
            },
            () => this.loadImportList(true),
        );
    }
}
