import * as React from 'react';

// Services
import { Injector } from '@angular/core';
import { ImportsService } from '../../resources/imports/imports.service';
import { AuthService } from '../../auth/auth.service';
import { Namespace } from '../../resources/namespaces/namespace';
import { ImportList, ImporterMessage } from '../../resources/imports/import';

// Components
import { ImportListComponent } from '../components/my-imports/import-list';
import { PageHeader } from '../components/page-header';
import { ImportConsoleComponent } from '../components/my-imports/import-console';

interface IProps {
    injector: Injector;
    namespaces: Namespace[];
    selectedNamespace?: Namespace;
    importList?: any;
    selectedImport?: any;
    selectedImportDetail?: any;
}

interface IState {
    selectedNS: Namespace;
    importList: ImportList[];
    selectedImport: ImportList;
    taskMessages: ImporterMessage[];
    followMessages: boolean;
}

export class MyImportsPage extends React.Component<IProps, IState> {
    importsService: ImportsService;
    authService: AuthService;

    constructor(props) {
        super(props);

        this.state = {
            selectedNS: this.props.selectedNamespace,
            importList: this.props.importList,
            selectedImport: this.props.selectedImport,
            taskMessages: [],
            followMessages: false,
        };
    }

    componentDidMount() {
        this.importsService = this.props.injector.get(ImportsService);
        this.authService = this.props.injector.get(AuthService);

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
                        />
                    </div>
                    <div className='col-sm-8'>
                        <ImportConsoleComponent
                            taskMessages={this.state.taskMessages}
                            followMessages={this.state.followMessages}
                            toggleFollowMessages={() =>
                                this.toggleFollowMessages()
                            }
                        />
                    </div>
                </div>
            </div>
        );
    }

    private toggleFollowMessages() {
        this.setState({ followMessages: !this.state.followMessages });
    }

    private loadSelectedNS() {
        if (this.state.selectedNS) {
            this.loadImportList();
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

    private loadImportList() {
        if (this.state.importList) {
            this.setState({ selectedImport: this.state.importList[0] }, () =>
                this.loadTaskMessages(),
            );
        } else {
            this.importsService
                .get_import_list(this.state.selectedNS.id)
                .subscribe(importList => {
                    this.setState(
                        {
                            importList: importList,
                            selectedImport: importList[0],
                        },
                        () => this.loadTaskMessages(),
                    );
                });
        }
    }

    private loadTaskMessages() {
        if (this.state.selectedImport.type === 'collection') {
            this.importsService
                .get_collection_import(this.state.selectedImport.id)
                .subscribe(result => {
                    this.setState({ taskMessages: result.messages });
                });
        } else if (this.state.selectedImport.type === 'repository') {
            // Map repo import messages so that they look like collection
            // messages
            this.importsService
                .get_repo_import(this.state.selectedImport.id)
                .subscribe(result => {
                    this.setState({
                        taskMessages: result.summary_fields.task_messages.map(
                            el => {
                                return {
                                    level: el.message_type,
                                    message: el.message_text,
                                    time: '',
                                };
                            },
                        ),
                    });
                });
        }
    }

    private selectImportDetail(item: ImportList) {
        this.setState({ selectedImport: item }, () => this.loadTaskMessages());
    }
}
