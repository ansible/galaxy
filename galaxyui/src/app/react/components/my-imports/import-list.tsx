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
    Paginator,
} from 'patternfly-react';

import {
    FilterConfig,
    FilterOption,
    AppliedFilter,
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

interface IState {
    selectedFilter: FilterOption;
    filterValue: string;
}

export class ImportListComponent extends React.Component<IProps, IState> {
    filterConfig: FilterConfig;

    constructor(props) {
        super(props);

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
                    placeholder: 'Filter by Content Type...',
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

        this.state = {
            selectedFilter: this.filterConfig.fields[0],
            filterValue: '',
        };
    }

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

        const pageNumber = Number(queryParams.page) || 1;
        const pageSize = Number(queryParams.page_size) || 10;

        // The applied filters on the filter widget are determined by the
        // page's query params, so rather than holding applied filters in state
        // we're going to dynamically generate it from query params each time
        // the page is re-rendered so as to maintain a definitive source of
        // truth for the page
        this.filterConfig.appliedFilters = [];
        for (const key of Object.keys(this.props.queryParams)) {
            const field = this.filterConfig.fields.find(x => x.id === key);
            if (field) {
                this.filterConfig.appliedFilters.push({
                    field: field,
                    value: this.props.queryParams[key],
                });
            }
        }

        return (
            <div className='import-list'>
                {this.renderNamespacePicker(namespaces, selectedNS)}
                <FilterPF
                    filterConfig={this.filterConfig}
                    addFilter={(v, f) => this.addFilter(v, f)}
                    field={this.state.selectedFilter}
                    value={this.state.filterValue}
                    updateParent={x => this.updateParent(x)}
                />

                {this.filterConfig.appliedFilters.length > 0 ? (
                    <ToolBarResultsPF
                        numberOfResults={numberOfResults}
                        appliedFilters={this.filterConfig.appliedFilters}
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

                <Paginator
                    viewType={'list'}
                    pagination={{
                        page: pageNumber,
                        perPage: pageSize,
                        perPageOptions: [10, 20, 40, 80, 100],
                    }}
                    itemCount={numberOfResults}
                    onPageSet={i => this.setPageNumber(i)}
                    onPerPageSelect={i => this.setPageSize(i)}
                />
            </div>
        );
    }

    private updateParent(state) {
        this.setState(state);
    }

    private setPageSize(size) {
        const params = cloneDeep(this.props.queryParams);

        params['page_size'] = size;
        params['page'] = 1;
        this.props.setQueryParams(params);
    }

    private setPageNumber(pageNum) {
        const params = cloneDeep(this.props.queryParams);
        params['page'] = pageNum;
        this.props.setQueryParams(params);
    }

    private addFilter(value: string, field: FilterOption) {
        // Check to see if an instance of the filter has already been added
        const params = cloneDeep(this.props.queryParams);
        params[field.id] = value;
        params['page'] = 1;

        this.props.setQueryParams(params);
    }

    private removeFilter(index) {
        const filter = this.filterConfig.appliedFilters[index.index];
        const params = cloneDeep(this.props.queryParams);
        delete params[filter.field.id];
        params['page'] = 1;

        this.props.setQueryParams(params);

        if (filter.field.id === this.state.selectedFilter.id) {
            this.setState({ filterValue: '' });
        }
    }

    private removeAllFilters() {
        const params = cloneDeep(this.props.queryParams);

        for (const field of this.filterConfig.fields) {
            delete params[field.id];
        }
        params['page'] = 1;

        this.props.setQueryParams(params);
        this.setState({ filterValue: '' });
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
                    Status: {item.state}{' '}
                    {item.finished_at
                        ? moment(item.finished_at).fromNow()
                        : null}
                </div>
            </div>
        );
    }

    private getStatusClass(state) {
        const statusClass = 'fa status-icon ';

        switch (state) {
            case PulpStatus.running:
                return statusClass + 'fa-spin fa-spinner color-green';
            case PulpStatus.waiting:
                return statusClass + 'fa-spin fa-spinner color-green';
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
            <div className='namespace-selector-wrapper'>
                <div className='label'>Namespace</div>
                <div className='selector'>
                    <FormControl
                        onChange={event =>
                            this.props.selectNamespace(event.target.value)
                        }
                        value={selectedNS.id}
                        componentClass='select'
                    >
                        {namespaces.map(ns => (
                            <option key={ns.id} value={ns.id}>
                                {ns.name}
                            </option>
                        ))}
                    </FormControl>
                </div>
            </div>
        );
    }
}
