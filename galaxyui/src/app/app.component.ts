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

import { Component, OnInit, TemplateRef } from '@angular/core';

import { NavigationEnd, NavigationStart, Router } from '@angular/router';

import { BsModalService } from 'ngx-bootstrap/modal';
import { BsModalRef } from 'ngx-bootstrap/modal/bs-modal-ref.service';

import { AboutModalConfig, AboutModalEvent } from 'patternfly-ng/modal';

import { VerticalNavigationItem } from 'patternfly-ng/navigation/vertical-navigation/vertical-navigation-item';
import { Notification } from 'patternfly-ng/notification';
import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';

import { AuthService } from './auth/auth.service';
import { ApiRootService } from './resources/api-root/api-root.service';

import { BodyCommand, PFBodyService } from './resources/pf-body/pf-body.service';

@Component({
    selector: 'galaxy-nav',
    styleUrls: ['./app.component.less'],
    templateUrl: './app.component.html',
})
export class AppComponent implements OnInit {
    constructor(
        private router: Router,
        private authService: AuthService,
        private apiRootService: ApiRootService,
        private modalService: BsModalService,
        private notificationService: NotificationService,
        private pfBodyService: PFBodyService,
    ) {
        this.router.events.subscribe(event => {
            if (event instanceof NavigationEnd || event instanceof NavigationStart) {
                // When user navigates away from a page, remove any lingering notifications
                const notices: Notification[] = this.notificationService.getNotifications();
                notices.forEach((notice: Notification) => {
                    this.notificationService.remove(notice);
                });
            }

            if (event instanceof NavigationStart) {
                this.isLoading = true;
            }

            if (event instanceof NavigationEnd) {
                this.isLoading = false;
            }
        });
    }

    navItems: VerticalNavigationItem[] = [];
    modalRef: BsModalRef;
    authenticated = false;
    username: string = null;
    showAbout = false;
    aboutConfig: AboutModalConfig;
    redirectUrl: string = null;
    teamMembers: string[];
    pfBody: any;
    isLoading = true;

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

        this.pfBodyService.currentMessage.subscribe((message: BodyCommand) => {
            this.pfBody[message.propertyName] = message.propertyValue;
        });

        // TODO add unsecured API endpoint for retrieving Galaxy version
        this.aboutConfig = {
            additionalInfo: '',
            copyright: '© Copyright 2018 Red Hat, Inc.',
            logoImageAlt: 'Ansible Galaxy',
            logoImageSrc: '/assets/galaxy-logo-03.svg',
            title: 'Galaxy',
            productInfo: [{ name: 'Server', value: window.location.host }],
        } as AboutModalConfig;
        this.navItems = [
            {
                title: 'Home',
                iconStyleClass: 'fa fa-home',
                url: '/home',
            },
            {
                title: 'Search',
                iconStyleClass: 'fa fa-search',
                url: '/search',
            },
            /*{
                title: 'Partners',
                iconStyleClass: 'fa fa-star',
                url: '/partners'
            },*/
            {
                title: 'Community',
                iconStyleClass: 'fa fa-users',
                url: '/community',
            },
        ] as VerticalNavigationItem[];

        this.apiRootService.get().subscribe(apiInfo => {
            this.aboutConfig.productInfo.push({ name: 'Server Version', value: apiInfo.server_version });
            this.aboutConfig.productInfo.push({ name: 'Version Name', value: apiInfo.version_name });
            this.aboutConfig.productInfo.push({ name: 'Api Version', value: apiInfo.current_version });

            this.teamMembers = apiInfo.team_members;
        });

        this.authService.me().subscribe(me => {
            this.authenticated = me.authenticated;
            this.username = me.username;
            if (this.authenticated) {
                this.aboutConfig.productInfo.push({
                    name: 'User Name',
                    value: me.username,
                });
                this.aboutConfig.productInfo.push({
                    name: 'User Role',
                    value: me.staff ? 'Staff' : 'User',
                });

                this.addContentButtons();
            } else {
                this.removeContentButtons();
            }
            this.optionallyAddMobileButtons();
        });
        this.redirectUrl = this.authService.redirectUrl;
    }

    about(template: TemplateRef<any>): void {
        this.modalRef = this.modalService.show(template);
    }

    closeAbout($event: AboutModalEvent): void {
        this.modalRef.hide();
    }

    removeContentButtons(): void {
        this.removeNavItem('My Content');
        this.removeNavItem('My Imports');
    }

    addContentButtons(): void {
        this.addNavItem({
            title: 'My Content',
            iconStyleClass: 'fa fa-list',
            url: '/my-content',
        } as VerticalNavigationItem);
        this.addNavItem({
            title: 'My Imports',
            iconStyleClass: 'fa fa-upload',
            url: '/my-imports',
        } as VerticalNavigationItem);
    }

    logout(): void {
        this.authenticated = false;
        this.authService.logout().subscribe(
            response => {
                this.router.navigate(['/home']);
            },
            error => {
                console.log(error);
            },
        );
        this.removeContentButtons();
    }

    onResize($event) {
        if ($event.target.innerWidth < 768) {
            this.addMobileButtons();
        } else {
            this.removeMobileButtons();
        }
    }

    onItemClicked($event: VerticalNavigationItem): void {
        if ($event.title === 'Logout') {
            this.logout();
        }
        this.removeMobileButtons();
        this.optionallyAddMobileButtons();
    }

    // private
    private addMobileButtons(): void {
        this.addNavItem({
            title: 'Documentation',
            iconStyleClass: 'fa pficon-catalog',
            url: '/docs/',
        } as VerticalNavigationItem);
        if (!this.authenticated) {
            this.addNavItem({
                title: 'Login',
                iconStyleClass: 'fa fa-sign-in',
                url: '/login',
            } as VerticalNavigationItem);
        } else {
            this.addNavItem({
                title: 'Logout',
                iconStyleClass: 'fa fa-sign-out',
                url: '',
            } as VerticalNavigationItem);
        }
    }

    private removeMobileButtons(): void {
        ['Login', 'Logout', 'Documentation'].forEach(item => {
            console.log('remove ' + item);
            this.removeNavItem(item);
        });
    }

    private removeNavItem(title: string) {
        let i: number = null;
        i = this.findNavItem(title);
        if (i !== null) {
            this.navItems.splice(i, 1);
        }
    }

    private addNavItem(item: VerticalNavigationItem) {
        let i: number = null;
        i = this.findNavItem(item.title);
        if (i === null) {
            this.navItems.push(item);
        }
    }
    private findNavItem(title: string): number {
        let i: number = null;
        this.navItems.forEach((item: VerticalNavigationItem, index: number) => {
            if (item['title'] === title) {
                i = index;
            }
        });
        return i;
    }

    private optionallyAddMobileButtons(): void {
        const layoutElement = document.getElementById('verticalNavLayout');
        const layoutWidth = parseInt(window.getComputedStyle(layoutElement).width, 10);
        if (layoutWidth <= 768) {
            this.addMobileButtons();
        }
    }
}
