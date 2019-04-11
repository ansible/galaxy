import * as React from 'react';
import { ImporterMessage, ImportList } from '../../../resources/imports/import';
import { OverlayTrigger, Tooltip } from 'patternfly-react';
import { Link } from '../../lib/link';
import { ContentFormatURLs } from '../../../enums/format';
import { ImportMetadata } from '../../shared-types/my-imports';

interface IProps {
    taskMessages: ImporterMessage[];
    followMessages: boolean;
    selectedImport: ImportList;
    importMetadata: ImportMetadata;

    toggleFollowMessages: () => void;
}

export class ImportConsoleComponent extends React.Component<IProps, {}> {
    lastImport: any;

    constructor(props) {
        super(props);

        this.lastImport = React.createRef();
    }

    render() {
        const { selectedImport, taskMessages } = this.props;

        if (!taskMessages || !selectedImport) {
            return (
                <div className='import-console'>
                    {selectedImport ? this.renderTitle(selectedImport) : null}
                    <div className='loading message-list'>
                        <div className='spinner spinner-inverse' />
                    </div>
                </div>
            );
        }

        if (this.props.followMessages) {
            this.lastImport.current.scrollIntoView({ behavior: 'smooth' });
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
                                <Tooltip id='scroll-top-bottom'>
                                    Scroll to end of log
                                </Tooltip>
                            }
                        >
                            <span
                                onClick={() =>
                                    this.props.toggleFollowMessages()
                                }
                                className='fa fa-arrow-circle-down clickable'
                            />
                        </OverlayTrigger>
                    </div>

                    {taskMessages.map((x, i) => {
                        return this.renderMessage(x, i);
                    })}

                    <div
                        className='message'
                        key={'last'}
                        ref={this.lastImport}
                    />
                </div>
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
                        to={`/${ContentFormatURLs[selectedImport.type]}/${
                            selectedImport.namespace.name
                        }/${selectedImport.name}`}
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
}
