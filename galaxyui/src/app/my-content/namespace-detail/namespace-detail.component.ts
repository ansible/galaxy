import {
    Component,
    Input,
    OnInit
} from '@angular/core';

import { ActivatedRoute, Router } from '@angular/router';

import { cloneDeep } from 'lodash';

import {
    FormBuilder,
    FormControl,
    FormGroup,
    Validators
} from '@angular/forms';

import { FilterConfig }          from 'patternfly-ng/filter/filter-config';
import { FilterEvent }           from 'patternfly-ng/filter/filter-event';
import { FilterField }           from 'patternfly-ng/filter/filter-field';
import { FilterType }            from 'patternfly-ng/filter/filter-type';
import { FilterComponent }       from 'patternfly-ng/filter/filter.component';

import { Me }                    from '../../auth/auth.service';
import { Namespace }             from '../../resources/namespaces/namespace';
import { NamespaceService }      from '../../resources/namespaces/namespace.service';
import { ProviderNamespace }     from '../../resources/provider-namespaces/provider-namespace';
import { ProviderSource }        from '../../resources/provider-namespaces/provider-source';
import { ProviderSourceService } from '../../resources/provider-namespaces/provider-source.service';
import { User }                  from '../../resources/users/user';
import { UserService }           from '../../resources/users/user.service';

class Owner {
    username: string;
    github_user: string;
    id: number;
    avatar_url: string;
    selected: boolean;
}

class Source {
    description: string;
    html_url: string;
    id: number;
    display_name: string;
    name: string;
    company: string;
    avatar_url: string;
    location: string;
    provider: number;
    provider_name: string;
    email: string;
}

@Component({
    selector: 'app-namespace-detail',
    templateUrl: './namespace-detail.component.html',
    styleUrls: ['./namespace-detail.component.less']
})
export class NamespaceDetailComponent implements OnInit {

    @Input()
    set namespace(data: Namespace) {
        this._namespace = data;
    }

    get namespace(): Namespace {
        return this._namespace;
    }

    _namespace: Namespace;
    me: Me;

    pageTitle = 'My Content;/my-content;Add Namespace';
    pageIcon = 'fa fa-list';
    pageLoading = true;


    namespaceForm: FormGroup;
    namespaceFilterConfig: FilterConfig;
    userFilterConfig: FilterConfig;

    users: User[] = [];
    selectedUsers: Owner[] = [];
    providerSources: ProviderSource[];
    providerSourcesFiltered: ProviderSource[];
    selectedNamespaces: Source[] = [];
    usersLoading = true;
    namespacesLoading = true;

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private formBuilder: FormBuilder,
        private namespaceService: NamespaceService,
        private userService: UserService,
        private providerSourceService: ProviderSourceService
    ) {}

    ngOnInit() {
        this.route.data
            .subscribe(data => {
                this.me = data['me'];
                this.namespace = new Namespace();
                this.pageLoading = false;
                if (data['namespace']) {
                    this.namespace = data['namespace'];
                    if (this.namespace && this.namespace['summary_fields']) {
                        this.selectedUsers = this.namespace.summary_fields['owners'] as Owner[];
                        this.selectedNamespaces = this.namespace.summary_fields['provider_namespaces'] as Source[];
                        this.pageTitle = 'My Content;/my-content;Edit Namespace';
                    } else {
                        // Requested namespace not found
                        this.router.navigate(['/not-found']);
                    }
                }
                this.createForm();
                this.getUsers();
                this.getProviderSources();
            });

        this.namespaceFilterConfig = {
            fields: [{
                id: 'name',
                title: 'Name',
                placeholder: 'Filter by Name',
                type: FilterType.TEXT
            }] as FilterField[],
            resultsCount: 0,
            appliedFilters: []
        } as FilterConfig;

        this.userFilterConfig = {
            fields: [{
                id: 'name',
                title: 'Name',
                placeholder: 'Filter by Name',
                type: FilterType.TEXT
            }] as FilterField[],
            resultsCount: 0,
            appliedFilters: []
        } as FilterConfig;
    }

    saveNamespace($event) {
        const namespace: Namespace = this.prepareSaveNamespace();
        this.namespaceService.save(namespace)
            .subscribe(
                result => {
                    if (!this.namespaceService.encounteredErrors) {
                        this.router.navigate(['/my-content']);
                    }
                }
            );
    }

    toggleUser(id: number): void {
        let match = false;
        let matchedIdx = -1;
        let user: User;

        this.users.forEach(item => {
            if (item.id === id) {
                user = item;
            }
        });

        if (user) {
            user.selected = !user.selected;
        }

        this.selectedUsers.forEach((owner: User, idx: number) => {
            if (owner.id === id) {
                match = true;
                matchedIdx = idx;
            }
        });

        if (!match && user && user.selected) {
            // add selected user
            this.selectedUsers.push(user);
        }
        if (match && (!user || !user.selected) && matchedIdx > -1) {
            // remove deselected user
            this.selectedUsers.splice(matchedIdx, 1);
        }
    }

    toggleNamespace(name: string, provider: number): void {
        let match = false;
        let matchedIdx = -1;
        let namespace: ProviderSource;

        this.providerSources.forEach(item => {
            if (item.name === name && item.provider === provider) {
                namespace = item;
            }
        });

        namespace.selected = !namespace.selected;

        this.selectedNamespaces.forEach((ns: Source, idx: number) => {
            if (ns.name === namespace.name && ns.provider === namespace.provider) {
                match = true;
                matchedIdx = idx;
            }
        });

        if (!match && namespace.selected) {
            // add selected namespace
            const source = new Source();
            source.description = namespace.description;
            source.html_url = namespace.html_url;
            source.display_name = namespace.display_name;
            source.name = namespace.name;
            source.company = namespace.company;
            source.avatar_url = namespace.avatar_url;
            source.location = namespace.location;
            source.provider = namespace.provider;
            source.provider_name = namespace.provider_name;
            source.email = namespace.email;
            this.selectedNamespaces.push(source);
        }
        if (match && !namespace.selected && matchedIdx > -1) {
            // remove deselected user
            this.selectedNamespaces.splice(matchedIdx, 1);
        }
    }

    namespaceFilterChanged($event: FilterEvent): void {
        if (!$event.appliedFilters.length) {
            this.providerSourcesFiltered = cloneDeep(this.providerSources);
            this.namespaceFilterConfig.resultsCount = 0;
        } else {
            this.providerSourcesFiltered = [];
            this.providerSources.forEach(source => {
                $event.appliedFilters.forEach(filter => {
                    if (source[filter.field.id].indexOf(filter.value) > -1) {
                        this.providerSourcesFiltered.push(source);
                    }
                });
            });
            this.namespaceFilterConfig.resultsCount = this.providerSourcesFiltered.length;
        }
    }

    userFilterChanged($event: FilterEvent): void {
        if ($event.appliedFilters.length) {
            let queryStr = '';
            $event.appliedFilters.forEach((filter: any, idx: number) => {
                if (idx > 0) {
                    queryStr += '&';
                }
                queryStr += `or__username__icontains=${filter.value}`;
            });
            this.getUsers(queryStr);
        } else {
            this.getUsers();
        }
    }


    // private

    private createForm() {
        this.namespaceForm = this.formBuilder.group({
            name: [this.namespace.name, Validators.required],
            description: [this.namespace.description, Validators.required],
            company: [this.namespace.company],
            location: [this.namespace.location],
            avatar_url: [this.namespace.avatar_url],
            email: [this.namespace.email],
            html_url: [this.namespace.html_url],
            namespaceType: (this.namespace.is_vendor) ? ['vendor'] : ['community']
        });
        if (!this.me.staff) {
            this.namespaceForm.controls['namespaceType'].disable();
            this.namespaceForm.controls['name'].disable();
        }
    }

    private getUsers(params?: any): void {
        this.usersLoading = true;
        this.userService.query(params)
            .subscribe(
                users => {
                    this.users = this.prepUsersForList(users);
                    this.userFilterConfig.resultsCount = this.users.length;
                    this.usersLoading = false;
                }
            );
    }

    private getProviderSources(): void {
        this.namespacesLoading = true;
        this.providerSourceService.query()
            .subscribe(
                providerSources => {
                    this.providerSources = this.prepProviderSourcesForList(providerSources);
                    this.providerSourcesFiltered = this.providerSources;
                    this.namespacesLoading = false;
                }
            );
    }

    private prepUsersForList(users: User[]): User[] {
        const clone = cloneDeep(users);
        clone.forEach(item => {
            if (!item.avatar_url) {
                item.avatar_url = '/assets/avatar.png';
            }
            item.selected = false;
            this.selectedUsers.forEach(selected => {
                if (selected.id === item.id) {
                    item.selected = true;
                }
            });
        });
        return clone;
    }

    private prepProviderSourcesForList(providerSources: ProviderSource[]): ProviderSource[] {
        const clone = cloneDeep(providerSources);
        clone.forEach(item => {
            if (!item.avatar_url) {
                item.avatar_url = '/assets/avatar.png';
            }
            item.selected = false;
            this.selectedNamespaces.forEach(selected => {
                if (selected.provider === item.provider && selected.name === item.name) {
                    item.selected = true;
                }
            });
        });
        return clone;
    }

    private prepareSaveNamespace(): Namespace {
        const formModel = this.namespaceForm.value;
        const ns: Namespace = new Namespace();

        if (this.namespace.id) {
            ns.id = this.namespace.id;
        }
        ns.name = formModel.name as string;
        ns.description = formModel.description as string;
        ns.company = formModel.company as string;
        ns.location = formModel.location as string;
        ns.avatar_url = formModel.avatar_url as string;
        ns.email = formModel.email as string;
        ns.html_url = formModel.html_url as string;
        ns.active = true;
        ns.is_vendor = (formModel.namespaceType === 'vendor') ? true : false;

        const owners: User[] = [];
        const pns: ProviderNamespace[] = [];
        this.selectedUsers.forEach(item => {
            const owner: User = new User();
            owner.id = item.id;
            owners.push(owner);
        });
        this.selectedNamespaces.forEach(item => {
            const pn: ProviderNamespace = new ProviderNamespace();
            pn.description = item.description;
            pn.html_url = item.html_url;
            pn.display_name = item.display_name;
            pn.name = item.name;
            pn.company = item.company;
            pn.avatar_url = item.avatar_url;
            pn.location = item.location;
            pn.provider = item.provider;
            pn.provider_name = item.provider_name;
            pn.email = item.email;
            pns.push(pn);
        });
        ns.owners = owners;
        ns.provider_namespaces = pns;
        return ns;
    }
}
