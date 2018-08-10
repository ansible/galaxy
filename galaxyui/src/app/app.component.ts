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
    NavigationStart,
    NavigationEnd
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
import { ApiRootService }       from './resources/api-root/api-root.service';
import { ApiRoot }              from './resources/api-root/api-root';


import {
    BodyCommand,
    PFBodyService
} from './resources/pf-body/pf-body.service';

@Component({
    selector: 'galaxy-nav',
    styleUrls:   ['./app.component.less'],
    templateUrl: './app.component.html'
})
export class AppComponent implements OnInit {

    constructor(
        private router:       Router,
        private authService:  AuthService,
        private apiRootService: ApiRootService,
        private modalService: BsModalService,
        private notificationService: NotificationService,
        private pfBodyService: PFBodyService,
    ) {
        this.router.events.subscribe(event => {
            if (event instanceof NavigationEnd || event instanceof NavigationStart) {
                // When user navigates away from a page, remove any lingering notifications
                const notices: Notification[] = notificationService.getNotifications();
                notices.forEach((notice: Notification) => {
                    notificationService.remove(notice);
                });
            }
        });
    }

    navItems:      NavigationItemConfig[] = [];
    modalRef:      BsModalRef;
    authenticated = false;
    username:      string = null;
    showAbout = false;
    aboutConfig:   AboutModalConfig;
    redirectUrl:   string = null;
    teamMembers:   string[];
    pfBody: any;

    ngOnInit(): void {
        // Patternfly embeds everything not related to navigation in a div with
        // it's own scrollbar. This means that the window never scrolls and the
        // browser thinks that the scroll height of the window is always 0.
        // Therefore, in order to scroll the page programatically, we need to
        // scroll the div that contains the main body of the web app. Child
        // components can't access this div directly, because it's part of
        // app.component, so requests to scroll the div have to be routed through
        // this service.

        this.pfBody = document.getElementById('pfContentBody');

        this.pfBodyService.currentMessage.subscribe(
            (message: BodyCommand) => {
                this.pfBody[message.propertyName] = message.propertyValue;
            }
        );

        // TODO add unsecured API endpoint for retrieving Galaxy version
        this.aboutConfig = {
            additionalInfo: '',
            copyright: '© Copyright 2018 Red Hat, Inc.',
            logoImageAlt: 'Ansible Galaxy',
            logoImageSrc: '/assets/galaxy-logo-03.svg',
            title: 'Galaxy',
            productInfo: [
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
            /*{
                title: 'Partners',
                iconStyleClass: 'fa fa-star',
                url: '/partners'
            },*/
            {
                title: 'Community',
                iconStyleClass: 'fa fa-users',
                url: '/community'
            },
        ] as NavigationItemConfig[];

        this.apiRootService.get().subscribe(
            (apiInfo) => {
                this.aboutConfig.productInfo.push({name: 'Server Version', value: apiInfo.server_version });
                this.aboutConfig.productInfo.push({name: 'Version Name', value: apiInfo.version_name});
                this.aboutConfig.productInfo.push({name: 'Api Version', value: apiInfo.current_version });

                this.teamMembers = apiInfo.team_members;
            }
        );

        this.authService.me().subscribe(
            (me) => {
                this.authenticated = me.authenticated;
                this.username = me.username;
                if (this.authenticated) {

                    this.aboutConfig.productInfo.push({
                        name: 'User Name',
                        value: me.username
                    });
                    this.aboutConfig.productInfo.push({
                        name: 'User Role',
                        value: (me.staff) ? 'Staff' : 'User'
                    });

                    this.addNavButtons();
                } else {
                    this.removeNavButtons();
                }
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

    removeNavButtons(): void {
        for (let i = 0; i < this.navItems.length; i++) {
            const title = this.navItems[i].title;
            if (title === 'My Content' || title === 'My Imports') {
                this.navItems.splice(i, 1);
                i--;
            }
        }
    }

    addNavButtons(): void {
        this.navItems.push(
            {
                title: 'My Content',
                iconStyleClass: 'fa fa-list',
                url: '/my-content'
            },
            {
                title: 'My Imports',
                iconStyleClass: 'fa fa-upload',
                url: '/my-imports'
            }
        );
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
        this.removeNavButtons();
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
