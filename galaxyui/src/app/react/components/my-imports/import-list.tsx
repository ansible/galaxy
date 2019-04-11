import * as React from 'react';
import * as moment from 'moment';

import { ImportList } from '../../../resources/imports/import';
import { Namespace } from '../../../resources/namespaces/namespace';

import { ListView, ListViewItem } from 'patternfly-react';

import { PulpStatus } from '../../../enums/import-state.enum';

interface IProps {
    namespaces: Namespace[];
    selectedNS: Namespace;
    importList: ImportList[];
    selectedImport: ImportList;

    selectImport: (x) => void;
}

export class ImportListComponent extends React.Component<IProps, {}> {
    render() {
        const { selectImport, importList, selectedImport } = this.props;

        if (importList) {
            return (
                <ListView>
                    {importList.map(item => {
                        return (
                            <ListViewItem
                                onClick={() => selectImport(item)}
                                initExpanded={false}
                                key={item.type + item.id}
                                className={
                                    item.type === selectedImport.type &&
                                    item.id === selectedImport.id
                                        ? 'clickable selected-item'
                                        : 'clickable'
                                }
                                leftContent={
                                    <i
                                        className={this.getStatusClass(
                                            item.state,
                                        )}
                                    />
                                }
                                heading={this.renderDescription(item)}
                            />
                        );
                    })}
                </ListView>
            );
        } else {
            return null;
        }
    }

    renderDescription(item) {
        return (
            <div>
                <div>
                    {item.name} {item.version ? 'v' + item.version : ''}
                </div>
                <div className='sub-text'>
                    Status: {item.state} {moment(item.finished_at).fromNow()}
                </div>
            </div>
        );
    }

    getStatusClass(state) {
        const statusClass = 'fa status-icon ';

        switch (state) {
            case PulpStatus.running:
                return statusClass + 'fa-spinner color-orange';
            case PulpStatus.waiting:
                return statusClass + 'fa-spinner color-orange';
            case PulpStatus.completed:
                return statusClass + 'fa-circle color-green';
            default:
                return statusClass + 'fa-circle color-red';
        }
    }
}
