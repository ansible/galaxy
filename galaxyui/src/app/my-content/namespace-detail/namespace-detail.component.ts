import { Component, Input, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

import { cloneDeep } from 'lodash';

import {
    FormBuilder,
    FormControl,
    FormGroup,
    Validators
} from '@angular/forms';

import { Namespace }         from '../../resources/namespaces/namespace';

import { NamespaceService }      from "../../resources/namespaces/namespace.service";
import { UserService }           from "../../resources/users/user.service";
import { User }                  from "../../resources/users/user";
import { ProviderNamespace }     from "../../resources/provider-namespaces/provider-namespace";
import { ProviderSourceService } from "../../resources/provider-namespaces/provider-source.service";


@Component({
    selector: 'app-namespace-detail',
    templateUrl: './namespace-detail.component.html',
    styleUrls: ['./namespace-detail.component.less']
})
export class NamespaceDetailComponent implements OnInit {
    @Input() namespace: Namespace;

    namespaceForm: FormGroup;
    // namespace: Namespace = new Namespace();
    users: User[];
    providerSources: ProviderNamespace[];
    id: number;

    constructor(private route: ActivatedRoute,
                private router: Router,
                private formBuilder: FormBuilder,
                private namespaceService: NamespaceService,
                private userService: UserService,
                private providerSourceService: ProviderSourceService) {
    }

    ngOnInit() {
        this.route.data
            .subscribe((data: { namespace: Namespace }) => {
                this.namespace = data.namespace ? data.namespace : new Namespace();
                console.log('namespace detail ngOnInit', this.namespace);
                this.createForm();
            });

        this.getUsers();
        this.getProviderSources();
    }

    createForm() {
        this.namespaceForm = this.formBuilder.group({
            name: [this.namespace.name, Validators.required],
            description: [this.namespace.description, Validators.required],
            company: [this.namespace.company],
            location: [this.namespace.location],
            avatar_url: [this.namespace.avatar_url],
            email: [this.namespace.email],
            html_url: [this.namespace.html_url],
            owners: [this.namespace.owners],
            provider_namespaces:[this.namespace.provider_namespaces]
        })
    }

    saveNamespace() {
        console.log('saveNamespace');
        let namespace: Namespace = this.prepareSaveNamespace();
        this.namespaceService
            .save(namespace)
            .subscribe(_ => {
                this.router.navigate(['/my-content']);
            });
    }

    private getUsers(): void {
        this.userService.query()
            .subscribe(users => this.users = this.prepUsersForList(users));
    }

    private getProviderSources(): void {
        this.providerSourceService.query()
            .subscribe(providerSources => this.providerSources = this.prepProviderSourcesForList(providerSources));
    }

    private prepUsersForList(users: User[]): User[] {
        let clone = cloneDeep(users);

        //TODO transform for view?

        return clone;
    }

    private prepProviderSourcesForList(providerSources: ProviderNamespace[]): ProviderNamespace[] {
        let clone = cloneDeep(providerSources);

        //TODO transform for view?

        return clone;
    }

    private prepareSaveNamespace(): Namespace {
        const formModel = this.namespaceForm.value;

        let n: Namespace = new Namespace();

        if (this.namespace.id) {
            n.id = this.namespace.id;
        }
        n.name = formModel.name as string;
        n.description = formModel.description as string;
        n.company = formModel.company as string;
        n.location = formModel.location as string;
        n.avatar_url = formModel.avatar_url as string;
        n.email = formModel.email as string;
        n.html_url = formModel.html_url as string;
        n.active = true;
        n.owners = formModel.owners as User[];
        n.provider_namespaces = formModel.provider_namespaces as ProviderNamespace[];

        return n;
    }
}
