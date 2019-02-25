import * as React from 'react';

interface IProps {
    file: File;
    errors: string;
    uploadProgress: number;
    uploadStatus: string;
    handeFileUpload: (files: FileList) => void;
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
                                {this.renderFileIcon()}
                            </div>
                            <div className='upload-text'>
                                {this.props.file != null
                                    ? this.props.file.name
                                    : 'Select file'}
                                <div
                                    className='loading-bar'
                                    style={{
                                        width:
                                            this.props.uploadProgress * 100 +
                                            '%',
                                    }}
                                />
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

    renderFileIcon() {
        switch (this.props.uploadStatus) {
            case 'uploading':
                return <i className='fa fa-spinner fa-spin' />;
            default:
                return <i className='pficon-folder-open' />;
        }
    }
}
