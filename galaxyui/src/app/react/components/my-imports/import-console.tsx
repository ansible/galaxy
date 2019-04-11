import * as React from 'react';
import { ImporterMessage } from '../../../resources/imports/import';
import { OverlayTrigger, Tooltip } from 'patternfly-react';

interface IProps {
    taskMessages: ImporterMessage[];
    followMessages: boolean;

    toggleFollowMessages: () => void;
}

export class ImportConsoleComponent extends React.Component<IProps, {}> {
    lastImport: any;

    constructor(props) {
        super(props);

        this.lastImport = React.createRef();
    }

    render() {
        if (this.props.followMessages) {
            this.lastImport.current.scrollIntoView({ behavior: 'smooth' });
        }
        return (
            <div>
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

                    {this.props.taskMessages.map((x, i) => {
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
}
