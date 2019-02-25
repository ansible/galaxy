import * as React from 'react';
import { Button } from 'patternfly-react';
import { View } from '../../shared-types/add-repository';

interface IProps {
    setView: (v: View) => void;
}

export class PickImportType extends React.Component<IProps, {}> {
    render() {
        return (
            <div className='add-content-type-selector'>
                <div className='button-container'>
                    <Button
                        bsSize='large'
                        onClick={() => this.props.setView(View.RepoImport)}
                    >
                        <i className='fa fa-github' /> Import from GitHub
                    </Button>

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
                </div>
            </div>
        );
    }
}
