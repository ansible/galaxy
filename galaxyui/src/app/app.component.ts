import {
  Component,
  OnInit,
  TemplateRef }                 from '@angular/core';

import { Router }               from '@angular/router';
import { DOCUMENT }             from '@angular/common';

import { BsModalService }       from 'ngx-bootstrap/modal';
import { BsModalRef }           from 'ngx-bootstrap/modal/bs-modal-ref.service';

import { NavigationItemConfig } from 'patternfly-ng/navigation/navigation-item-config';
import { AboutModalConfig }     from 'patternfly-ng/modal/about-modal-config';
import { AboutModalEvent }      from 'patternfly-ng/modal/about-modal-event';

import { AuthService }          from './auth/auth.service';

@Component({
    selector: 'galaxy-nav',
    styleUrls:   ['./app.component.less'],
    templateUrl: './app.component.html'
})
export class AppComponent {

    navigationItems: NavigationItemConfig[];

    constructor(
        private router:       Router,
        private authService:  AuthService,
        private modalService: BsModalService
    ) {}

    modalRef:      BsModalRef;
    authenticated: boolean = false;
    username:      string = null;
    showAbout:     boolean = false;
    aboutConfig:   AboutModalConfig;

    ngOnInit(): void {
        this.navigationItems = [
            {
                title: 'Dashboard',
                iconStyleClass: 'fa fa-dashboard',
                url: '/navigation/dashboard'
            },
            {
                title: 'Dolor',
                iconStyleClass: 'fa fa-shield',
                url: '/navigation/dolor',
                badges: [
                    {
                        count: 1283,
                        tooltip: 'Total number of items'
                    }
                ]
            },
            {
                title: 'Ipsum',
                iconStyleClass: 'fa fa-space-shuttle',
                children: [
                    {
                        title: 'Intellegam',
                        children: [
                            {
                                title: 'Recteque',
                                url: '/navigation/ipsum/intellegam/recteque',
                                badges: [
                                    {
                                        count: 6,
                                        tooltip: 'Total number of error items',
                                        badgeClass: 'example-error-background'
                                    }
                                ]
                            },
                            {
                                title: 'Suavitate',
                                url: '/navigation/ipsum/intellegam/suavitate',
                                badges: [
                                    {
                                        count: 2,
                                        tooltip: 'Total number of items'
                                    }
                                ]
                            },
                            {
                                title: 'Vituperatoribus',
                                url: '/navigation/ipsum/intellegam/vituperatoribus',
                                badges: [
                                    {
                                        count: 18,
                                        tooltip: 'Total number of warning items',
                                        badgeClass: 'example-warning-background'
                                    }
                                ]
                            }
                        ]
                    }
                ]
             },
            {
                title: 'My Content',
                iconStyleClass: 'fa fa-book',
                url: '/my-content'
            },
            {
                title: 'Experiment',
                iconStyleClass: 'fa fa-flask',
                url: '/experiment'
            }
        ];
        // TODO add unsecured API endpoint for retrieving Galaxy version
        this.aboutConfig = {
            additionalInfo: '',
            copyright: '© Copyright 2018 Red Hat, Inc.',
            logoImageAlt: '',
            logoImageSrc: '',
            title: 'Galaxy',
            productInfo: [
                { name: 'Version', value: '????' },
                { name: 'Server', value: window.location.host }
            ]
        } as AboutModalConfig;

        this.authService.me().subscribe(
            (me) => {
                this.authenticated = me.authenticated;
                this.username = me.username;
                this.aboutConfig.productInfo.push({
                    name: 'User Name',
                    value: me.username
                });
                this.aboutConfig.productInfo.push({
                    name: 'User Role',
                    value: (me.staff) ? 'Staff' : 'User'
                });
            }
        );
    }

    about(template: TemplateRef<any>): void {
        this.modalRef = this.modalService.show(template);
    }

    closeAbout($event: AboutModalEvent): void {
        this.modalRef.hide();
    }
}
