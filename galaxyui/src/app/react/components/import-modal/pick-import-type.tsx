import * as React from 'react';
import { Button, OverlayTrigger, Tooltip } from 'patternfly-react';
import { View } from '../../shared-types/add-repository';

interface IProps {
    setView: (v: View) => void;
}

export class PickImportType extends React.Component<IProps, {}> {
    render() {
        return (
            <div className='add-content-type-selector'>
                <div className='button-container'>
                    <OverlayTrigger
                        overlay={
                            <Tooltip id='repository'>
                                Legacy Role import. Does not support Collection
                                format.
                            </Tooltip>
                        }
                        placement='top'
                        trigger={['hover', 'focus']}
                        rootClose={false}
                    >
                        <Button
                            bsSize='large'
                            onClick={() => this.props.setView(View.RepoImport)}
                        >
                            <i className='fa fa-github' /> Import Role from
                            GitHub
                        </Button>
                    </OverlayTrigger>

                    <OverlayTrigger
                        overlay={
                            <Tooltip id='collection'>
                                Used for distributing Galaxy hosted roles,
                                modules and plugins.
                            </Tooltip>
                        }
                        placement='top'
                        trigger={['hover', 'focus']}
                        rootClose={false}
                    >
                        <Button
                            className='right-button'
                            bsSize='large'
                            onClick={() =>
                                this.props.setView(View.CollectionImport)
                            }
                        >
                            <i className='pficon-folder-open' /> Upload New
                            Collection
                        </Button>
                    </OverlayTrigger>
                </div>
            </div>
        );
    }
}
