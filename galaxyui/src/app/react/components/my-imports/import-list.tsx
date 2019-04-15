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

import {
    FilterConfig,
    FilterOption,
    AppliedFilter,
    SortConfig,
} from '../../shared-types/pf-toolbar';

import { FilterPF, ToolBarResultsPF } from '../patternfly-filter';

import { PulpStatus } from '../../../enums/import-state.enum';

import { cloneDeep } from 'lodash';

interface IProps {
    namespaces: Namespace[];
    selectedNS: Namespace;
    importList: ImportList[];
    selectedImport: ImportList;
    noImportsExist: boolean;
    numberOfResults: number;
    queryParams: any;

    selectImport: (x) => void;
    selectNamespace: (ns) => void;
    setQueryParams: (filters) => void;
}

export class ImportListComponent extends React.Component<IProps, {}> {
    appliedFilters = [] as AppliedFilter[];
    filterConfig = {} as FilterConfig;

    render() {
        const {
            selectImport,
            importList,
            selectedImport,
            selectedNS,
            namespaces,
            noImportsExist,
            numberOfResults,
            queryParams,
        } = this.props;

        this.filterConfig = {
            fields: [
                {
                    id: 'name',
                    title: 'Name',
                    placeholder: 'Filter by Name...',
                    type: 'text',
                },
                {
                    id: 'type',
                    title: 'Type',
                    placeholder: 'Filter by Collection Type...',
                    type: 'select',
                    options: [
                        { id: 'collection', title: 'Collection' },
                        { id: 'repository', title: 'Repository' },
                    ],
                },
            ] as FilterOption[],
            resultsCount: 0,
            appliedFilters: [] as AppliedFilter[],
        } as FilterConfig;

        this.appliedFilters = [];

        for (const key of Object.keys(queryParams)) {
            const field = this.filterConfig.fields.find(x => x.id === key);
            if (field) {
                this.appliedFilters.push({
                    field: field,
                    value: queryParams[key],
                });
            }
        }

        return (
            <div>
                {this.renderNamespacePicker(namespaces, selectedNS)}
                <FilterPF
                    filterConfig={this.filterConfig}
                    addFilter={(v, f) => this.addFilter(v, f)}
                />

                {this.appliedFilters.length > 0 ? (
                    <ToolBarResultsPF
                        numberOfResults={numberOfResults}
                        appliedFilters={this.appliedFilters}
                        removeFilter={i => this.removeFilter(i)}
                        removeAllFilters={() => this.removeAllFilters()}
                    />
                ) : null}

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

    addFilter(value: string, field: FilterOption) {
        // // Check to see if an instance of the filter has already been added
        const params = cloneDeep(this.props.queryParams);
        params[field.id] = value;

        this.props.setQueryParams(params);
    }

    removeFilter(index) {
        const filter = this.appliedFilters[index.index];
        const params = cloneDeep(this.props.queryParams);
        delete params[filter.field.id];

        this.props.setQueryParams(params);
    }

    removeAllFilters() {
        const params = cloneDeep(this.props.queryParams);

        for (const field of this.filterConfig.fields) {
            delete params[field.id];
        }

        this.props.setQueryParams(params);
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
