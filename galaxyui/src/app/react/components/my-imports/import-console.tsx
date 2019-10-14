import * as React from 'react';
import { ImporterMessage, ImportList } from '../../../resources/imports/import';
import { OverlayTrigger, Tooltip } from 'patternfly-react';
import { Link } from '../../lib/link';
import { ImportMetadata } from '../../shared-types/my-imports';
import { PulpStatus } from '../../../enums/import-state.enum';

interface IProps {
    taskMessages: ImporterMessage[];
    followMessages: boolean;
    selectedImport: ImportList;
    importMetadata: ImportMetadata;
    noImportsExist: boolean;

    setFollowMessages: (follow: boolean) => void;
}

export class ImportConsoleComponent extends React.Component<IProps, {}> {
    lastImport: any;
    isLoading = false;

    constructor(props) {
        super(props);

        this.lastImport = React.createRef();
    }

    componentDidUpdate() {
        this.followLogs();
    }

    componentDidMount() {
        this.followLogs();
    }

    render() {
        const {
            selectedImport,
            taskMessages,
            noImportsExist,
            importMetadata,
        } = this.props;

        this.isLoading =
            importMetadata.state === PulpStatus.running ||
            importMetadata.state === PulpStatus.waiting;

        if (!taskMessages || !selectedImport) {
            return (
                <div className='import-console'>
                    {selectedImport ? this.renderTitle(selectedImport) : null}
                    <div className='loading message-list'>
                        {noImportsExist ? (
                            <div className='message'>No data</div>
                        ) : (
                            <div className='spinner spinner-inverse' />
                        )}
                    </div>
                </div>
            );
        }

        return (
            <div className='import-console'>
                {this.renderTitle(selectedImport)}
                <div className='message-list'>
                    <div
                        className={
                            this.props.followMessages
                                ? 'log-follow-button follow-active'
                                : 'log-follow-button'
                        }
                    >
                        <OverlayTrigger
                            placement='left'
                            overlay={
                                <Tooltip id='follow-logs'>
                                    {this.isLoading
                                        ? 'Follow Logs'
                                        : 'Scroll to End'}
                                </Tooltip>
                            }
                        >
                            <span
                                onClick={() => this.handleScrollClick()}
                                className='fa fa-arrow-circle-down clickable'
                            />
                        </OverlayTrigger>
                    </div>

                    {taskMessages.map((x, i) => {
                        return this.renderMessage(x, i);
                    })}

                    {taskMessages.length === 0 ? (
                        <div className='message'>
                            <span className='error'>
                                No task messages available
                            </span>
                        </div>
                    ) : null}
                </div>
                <div
                    className='last-message'
                    key={'last'}
                    ref={this.lastImport}
                />
            </div>
        );
    }

    renderMessage(item, i) {
        return (
            <div className='message' key={i}>
                <span className={item.level.toLowerCase()}>
                    {item.message}&nbsp;
                </span>
            </div>
        );
    }

    renderTitle(selectedImport) {
        const { importMetadata } = this.props;
        return (
            <div>
                <div className='title-container'>
                    <Link
                        className='title'
                        to={`/${selectedImport.namespace.name}/${selectedImport.name}`}
                    >
                        {selectedImport.namespace.name}.{selectedImport.name}
                    </Link>
                </div>

                <div className='title-bar'>
                    <div className='row'>
                        <div className='col-sm-10'>
                            <div>
                                <span className='data-title'>Status: </span>
                                {importMetadata.state}
                            </div>
                            {importMetadata.version ? (
                                <div>
                                    <span className='data-title'>
                                        Version:{' '}
                                    </span>
                                    {importMetadata.version}
                                </div>
                            ) : null}

                            {importMetadata.error ? (
                                <div>
                                    <span className='data-title'>
                                        Error Message:{' '}
                                    </span>
                                    {importMetadata.error}
                                </div>
                            ) : null}

                            {importMetadata.branch ? (
                                <div>
                                    <span className='data-title'>Branch: </span>
                                    {importMetadata.branch}
                                </div>
                            ) : null}

                            {importMetadata.commit_message ? (
                                <div>
                                    <span className='data-title'>
                                        Commit Message:{' '}
                                    </span>
                                    {importMetadata.commit_message}
                                </div>
                            ) : null}
                        </div>
                        <div className='col-sm-2'>
                            <div className='stats'>
                                {importMetadata.travis_build_url &&
                                importMetadata.travis_status_url ? (
                                    <div>
                                        <a
                                            href={
                                                importMetadata.travis_build_url
                                            }
                                            target='_blank'
                                        >
                                            <img
                                                src={
                                                    importMetadata.travis_status_url
                                                }
                                            />
                                        </a>
                                    </div>
                                ) : null}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    private handleScrollClick() {
        if (this.isLoading) {
            this.props.setFollowMessages(!this.props.followMessages);
        } else {
            this.lastImport.current.scrollIntoView({ behavior: 'smooth' });
        }
    }

    private followLogs() {
        if (this.props.followMessages && this.lastImport.current) {
            window.requestAnimationFrame(() => {
                this.lastImport.current.scrollIntoView({ behavior: 'smooth' });

                if (!this.isLoading) {
                    this.props.setFollowMessages(false);
                }
            });
        }
    }
}
