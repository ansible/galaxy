import * as React from 'react';
import { FieldGroup } from 'patternfly-react';

interface IProps {
    file: any;
    errors: string;
    handeFileUpload: (files) => void;
}

export class UploadCollection extends React.Component<IProps, {}> {
    render() {
        return (
            <div className='upload-collection'>
                <h4>Upload</h4>
                <form>
                    <input
                        className='upload-file'
                        type='file'
                        id='collection-widget'
                        onChange={e =>
                            this.props.handeFileUpload(e.target.files)
                        }
                    />
                    <label
                        className='upload-file-label'
                        htmlFor='collection-widget'
                    >
                        <div className='upload-box'>
                            <div className='upload-button'>
                                <i className='pficon-folder-open' />
                            </div>
                            <div className='upload-text'>
                                {this.props.file != null
                                    ? this.props.file.name
                                    : 'Select file'}
                            </div>
                        </div>
                    </label>
                </form>
                {this.props.errors ? (
                    <span className='file-error-messages'>
                        <i className='pficon-error-circle-o' />{' '}
                        {this.props.errors}
                    </span>
                ) : null}
            </div>
        );
    }
}
