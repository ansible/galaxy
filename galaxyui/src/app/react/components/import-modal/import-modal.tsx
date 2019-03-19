import * as React from 'react';

// Components
import { Button } from 'patternfly-react';
import { PageLoading } from '../page-loading';

import { ButtonConfig, View } from '../../shared-types/add-repository';

interface IProps {
    title: string;
    isSaving: boolean;
    buttonsDisplayed: ButtonConfig;
    disableOkay: boolean;
    close: () => void;
    save: () => void;
    setDisplayedContent: (v: View) => void;
}

export class ImportModal extends React.Component<IProps> {
    render() {
        return (
            <div className='add-repository-modal-wrapper'>
                {this.renderHeader()}
                <div className='modal-body add-repo-modal-body'>
                    <div className='container-fluid'>{this.props.children}</div>
                </div>
                {this.renderFooter()}
                <PageLoading loading={this.props.isSaving} />
            </div>
        );
    }

    private renderFooter() {
        return (
            <div className='modal-footer footer-container'>
                <div className='footer-buttons'>
                    {this.props.buttonsDisplayed.back ? (
                        <Button
                            onClick={() =>
                                this.props.setDisplayedContent(View.PickImport)
                            }
                        >
                            Back
                        </Button>
                    ) : null}
                </div>

                <div className='footer-buttons left-button'>
                    {this.props.buttonsDisplayed.okay.enabled ? (
                        <Button
                            disabled={this.props.disableOkay}
                            bsStyle='primary'
                            onClick={() => this.props.save()}
                        >
                            {this.props.buttonsDisplayed.okay.text}
                        </Button>
                    ) : null}

                    {this.props.buttonsDisplayed.cancel ? (
                        <Button bsStyle='warning' onClick={this.props.close}>
                            Cancel
                        </Button>
                    ) : null}
                </div>
            </div>
        );
    }

    private renderHeader() {
        return (
            <div className='modal-header'>
                <h4 className='modal-title pull-left'>{this.props.title}</h4>
                <button
                    type='button'
                    className='close pull-right'
                    aria-label='Close'
                    onClick={this.props.close}
                >
                    <span aria-hidden='true'>&times;</span>
                </button>
            </div>
        );
    }
}
