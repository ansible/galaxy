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

import { Component, OnInit, TemplateRef, ViewChild } from '@angular/core';

import { NavigationEnd, NavigationStart, Router } from '@angular/router';

import { BsModalService } from 'ngx-bootstrap/modal';
import { BsModalRef } from 'ngx-bootstrap/modal/bs-modal-ref.service';

import { VerticalNavigationItem } from 'patternfly-ng/navigation/vertical-navigation/vertical-navigation-item';
import {
    Notification,
    NotificationService,
    AboutModalConfig,
    AboutModalEvent,
    VerticalNavigationComponent,
} from 'patternfly-ng';

import { AuthService } from './auth/auth.service';
import { ApiRootService } from './resources/api-root/api-root.service';
import { EventLoggerService } from './resources/logger/event-logger.service';

import { NotificationDrawerComponent } from './utilities/notification-drawer/notification-drawer.component';

import {
    BodyCommand,
    PFBodyService,
} from './resources/pf-body/pf-body.service';

@Component({
    selector: 'galaxy-nav',
    styleUrls: ['./app.component.less'],
    templateUrl: './app.component.html',
})
export class AppComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'AppComponent';

    constructor(
        private router: Router,
        private authService: AuthService,
        private apiRootService: ApiRootService,
        private modalService: BsModalService,
        private notificationService: NotificationService,
        private pfBodyService: PFBodyService,
        private eventLogger: EventLoggerService,
    ) {
        this.router.events.subscribe(event => {
            if (
                event instanceof NavigationEnd ||
                event instanceof NavigationStart
            ) {
                // When user navigates away from a page, remove any lingering notifications
                const notices: Notification[] = this.notificationService.getNotifications();
                notices.forEach((notice: Notification) => {
                    this.notificationService.remove(notice);
                });
            }

            if (event instanceof NavigationStart) {
                this.isLoading = true;
                this.timeAtLoad = window.performance.now();
                this.startComponent = this.eventLogger.getComponentName();
                this.startUrl = this.router.url.split('?')[0];
            }

            if (event instanceof NavigationEnd) {
                this.isLoading = false;
                this.eventLogger.logPageLoad(
                    window.performance.now() - this.timeAtLoad,
                    this.startComponent,
                    this.startUrl,
                );
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
    timeAtLoad: number;
    startComponent: string;
    startUrl: string;

    unseenNotifications: boolean;

    @ViewChild(NotificationDrawerComponent)
    notificationList: NotificationDrawerComponent;

    @ViewChild(VerticalNavigationComponent)
    verticalNavigation: VerticalNavigationComponent;

    ngOnInit(): void {
        // Patternfly embeds everything not related to navigation in a div with
        // it's own scrollbar. This means that the window never scrolls and the
        // browser thinks that the scroll height of the window is always 0.
        // Therefore, in order to scroll the page programatically, we need to
        // scroll the div that contains the main body of the web app. Child
        // components can't access this div directly, because it's part of
        // app.component, so requests to scroll the div have to be routed through
        // this service.

        this.pfBody = document.getElementById('app-container');

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
            this.aboutConfig.productInfo.push({
                name: 'Server Version',
                value: apiInfo.server_version,
            });
            this.aboutConfig.productInfo.push({
                name: 'Version Name',
                value: apiInfo.version_name,
            });
            this.aboutConfig.productInfo.push({
                name: 'Api Version',
                value: apiInfo.current_version,
            });

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

            this.collapseNavOnSmallScreens(window.innerWidth);
        });
        this.redirectUrl = this.authService.redirectUrl;
    }

    setUnreadindicator(count) {
        this.unseenNotifications = count > 0;
    }

    toggleNotifcations() {
        this.notificationList.toggleNotifcations();
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

    collapseNavOnSmallScreens(screenWidth: number) {
        if (
            screenWidth < 1300 &&
            !this.verticalNavigation.navCollapsed &&
            !this.verticalNavigation.inMobileState
        ) {
            this.verticalNavigation.handleNavBarToggleClick();
        }
    }

    onItemClicked($event: VerticalNavigationItem): void {
        if ($event.title === 'Logout') {
            this.logout();
            this.removeMobileButtons();
            this.optionallyAddMobileButtons();
        }
        if ($event.title === 'Documentation') {
            window.location.pathname = '/docs/';
        }
        if ($event.title === 'Help') {
            window.location.href = 'https://github.com/ansible/galaxy/issues';
        }
    }

    // Updates the event logger so that it knows which component is currently
    // being loaded by the router outlet
    routerActivate($event) {
        this.eventLogger.setComponent($event.componentName);
    }

    // private
    private addMobileButtons(): void {
        this.addNavItem({
            title: 'Documentation',
            iconStyleClass: 'fa pficon-catalog',
            url: '',
            mobileItem: true,
        } as VerticalNavigationItem);
        this.addNavItem({
            title: 'Help',
            iconStyleClass: 'fa pficon-help',
            url: '',
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
        ['Documentation', 'Login', 'Logout', 'Help'].forEach(title => {
            this.removeNavItem(title);
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
        const layoutWidth = parseInt(
            window.getComputedStyle(layoutElement).width,
            10,
        );
        if (layoutWidth <= 768) {
            this.addMobileButtons();
        }
    }
}
