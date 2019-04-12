import * as React from 'react';
import * as moment from 'moment';

import { ImportList } from '../../../resources/imports/import';
import { Namespace } from '../../../resources/namespaces/namespace';

import {
    Col,
    Form,
    FormControl,
    FormGroup,
    ControlLabel,
    ListView,
    ListViewItem,
    EmptyState,
} from 'patternfly-react';

import { PulpStatus } from '../../../enums/import-state.enum';

interface IProps {
    namespaces: Namespace[];
    selectedNS: Namespace;
    importList: ImportList[];
    selectedImport: ImportList;
    noImportsExist: boolean;

    selectImport: (x) => void;
    selectNamespace: (ns) => void;
}

export class ImportListComponent extends React.Component<IProps, {}> {
    render() {
        const {
            selectImport,
            importList,
            selectedImport,
            selectedNS,
            namespaces,
            noImportsExist,
        } = this.props;

        return (
            <div>
                {this.renderNamespacePicker(namespaces, selectedNS)}
                <div>
                    {this.renderList(
                        selectImport,
                        importList,
                        selectedImport,
                        noImportsExist,
                    )}
                </div>
            </div>
        );
    }

    private renderList(
        selectImport,
        importList,
        selectedImport,
        noImportsExist,
    ) {
        if (noImportsExist) {
            return (
                <EmptyState>
                    <div>
                        <EmptyState.Icon name='info' />
                        <EmptyState.Title>No Imports</EmptyState.Title>

                        <EmptyState.Info>
                            There have not been any imports on this namespace
                        </EmptyState.Info>
                    </div>
                </EmptyState>
            );
        }

        if (!importList) {
            return (
                <div className='loading'>
                    <div className='spinner' />
                </div>
            );
        }

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
                                    className={this.getStatusClass(item.state)}
                                />
                            }
                            heading={this.renderDescription(item)}
                        />
                    );
                })}
            </ListView>
        );
    }

    private renderDescription(item) {
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

    private getStatusClass(state) {
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

    private renderNamespacePicker(namespaces, selectedNS) {
        if (!selectedNS) {
            return null;
        }
        return (
            <Form horizontal>
                <FormGroup>
                    <Col componentClass={ControlLabel} sm={2}>
                        Namespace
                    </Col>

                    <Col sm={10}>
                        <FormControl
                            value={selectedNS.id}
                            componentClass='select'
                        >
                            {namespaces.map(ns => (
                                <option
                                    key={ns.id}
                                    value={ns.id}
                                    onClick={() =>
                                        this.props.selectNamespace(ns)
                                    }
                                >
                                    {ns.name}
                                </option>
                            ))}
                        </FormControl>
                    </Col>
                </FormGroup>
            </Form>
        );
    }
}
