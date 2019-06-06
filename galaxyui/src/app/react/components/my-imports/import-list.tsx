import * as React from 'react';
import * as moment from 'moment';

import { ImportList } from '../../../resources/imports/import';
import { Namespace } from '../../../resources/namespaces/namespace';

import {
    FormControl,
    ListView,
    ListViewItem,
    EmptyState,
    Paginator,
} from 'patternfly-react';

import { FilterOption } from '../../shared-types/pf-toolbar';

import { ParamFilter } from '../param-filter';

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
    filterFields: FilterOption[];

    constructor(props) {
        super(props);

        this.filterFields = [
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
        ] as FilterOption[];
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

        return (
            <div className='import-list'>
                {this.renderNamespacePicker(namespaces, selectedNS)}
                <ParamFilter
                    filterFields={this.filterFields}
                    params={queryParams}
                    count={numberOfResults}
                    usePFToolbar={false}
                    updateParams={x => this.props.setQueryParams(x)}
                />

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
