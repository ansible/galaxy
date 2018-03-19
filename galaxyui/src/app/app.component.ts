/* (c) 2012-2018, Ansible by Red Hat
 *
 * This file is part of Ansible Galaxy
 *
 * Ansible Galaxy is free software: you can redistribute it and/or modify
 * it under the terms of the Apache License as published by
 * the Apache Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * Ansible Galaxy is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * Apache License for more details.
 *
 * You should have received a copy of the Apache License
 * along with Galaxy.  If not, see <http://www.apache.org/licenses/>.
 */

import {
  Component,
  OnInit,
  TemplateRef
} from '@angular/core';

import {
    Router,
    NavigationStart
} from '@angular/router';

import { DOCUMENT }             from '@angular/common';

import { BsModalService }       from 'ngx-bootstrap/modal';
import { BsModalRef }           from 'ngx-bootstrap/modal/bs-modal-ref.service';

import { NavigationItemConfig } from 'patternfly-ng/navigation/navigation-item-config';
import { AboutModalConfig }     from 'patternfly-ng/modal/about-modal-config';
import { AboutModalEvent }      from 'patternfly-ng/modal/about-modal-event';
import { NotificationService }  from 'patternfly-ng/notification/notification-service/notification.service';
import { Notification }         from 'patternfly-ng/notification';

import { AuthService }          from './auth/auth.service';

@Component({
    selector: 'galaxy-nav',
    styleUrls:   ['./app.component.less'],
    templateUrl: './app.component.html'
})
export class AppComponent {

    constructor(
        private router:       Router,
        private authService:  AuthService,
        private modalService: BsModalService,
        private notificationService: NotificationService
    ) {
        router.events.subscribe(
            event => {
                if (event instanceof NavigationStart) {
                    // When user navigates away from a page, remove any lingering notifications
                    let notices: Notification[] = notificationService.getNotifications();
                    if (notices) {
                        notices.forEach((notice: Notification) => {
                            notificationService.remove(notice);
                        });
                    }
                }
            }
        );
    }

    navItems:      NavigationItemConfig[] = [];
    modalRef:      BsModalRef;
    authenticated: boolean = false;
    username:      string = null;
    showAbout:     boolean = false;
    aboutConfig:   AboutModalConfig;
    redirectUrl:   string = null;

    ngOnInit(): void {
        console.log('init!');
        // TODO add unsecured API endpoint for retrieving Galaxy version
        this.aboutConfig = {
            additionalInfo: '',
            copyright: '© Copyright 2018 Red Hat, Inc.',
            logoImageAlt: 'Ansible Galaxy',
            logoImageSrc: '/assets/galaxy-brand-03.svg',
            title: 'Galaxy',
            productInfo: [
                { name: 'Version', value: '????' },
                { name: 'Server', value: window.location.host }
            ]
        } as AboutModalConfig;
        this.navItems = [
            {
                title: 'Home',
                iconStyleClass: 'fa fa-home',
                url: '/home'
            },
            {
                title: 'Search',
                iconStyleClass: 'fa fa-search',
                url: '/search'
            },
            {
                title: 'My Content',
                iconStyleClass: 'fa fa-book',
                url: '/my-content'
            },
            {
                title: 'My Imports',
                iconStyleClass: 'fa fa-upload',
                url: '/my-imports'
            }
        ];
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
        this.redirectUrl = this.authService.redirectUrl;
    }

    about(template: TemplateRef<any>): void {
        this.modalRef = this.modalService.show(template);
    }

    closeAbout($event: AboutModalEvent): void {
        this.modalRef.hide();
    }

    logout(): void {
        this.authenticated = false;
        this.authService.logout().subscribe(
            (response) => {
                this.router.navigate(['/home']);
            },
            (error) => {
                console.log(error);
            }
        );
    }

    onResize($event): void {
        console.log('window resized');
        console.log($event);
    }

    onItemClicked($event: NavigationItemConfig): void {
        console.log('item clicked');
        console.log($event);
    }

    onNavigation($event: NavigationItemConfig): void {
        console.log('navigation started');
        console.log($event);
    }
}
