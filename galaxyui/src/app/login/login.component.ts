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

import { Component, OnInit } from '@angular/core';

import { ActivatedRoute, ParamMap } from '@angular/router';

import { CardConfig } from 'patternfly-ng/card/basic-card/card-config';

import { Observable } from 'rxjs';

import { switchMap } from 'rxjs/operators';

import { AuthService } from '../auth/auth.service';

@Component({
    selector: 'login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.less'],
})
export class LoginComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'LoginComponent';

    config: CardConfig;
    msgText = 'Log into Galaxy by clicking on one of the above SCMs';
    connectingMsg = '';
    errorParam: Observable<boolean>;
    redirectUrl: string = null;

    constructor(
        private authService: AuthService,
        private route: ActivatedRoute,
    ) {}

    ngOnInit() {
        this.config = {
            noPadding: true,
            topBorder: false,
        } as CardConfig;

        this.route.queryParams.subscribe(params => {
            if (params.next) {
                this.redirectUrl = params.next;
            } else {
                this.redirectUrl = this.authService.redirectUrl;
            }
        });

        this.errorParam = this.route.paramMap.pipe(
            switchMap((params: ParamMap) => {
                return new Observable<boolean>(observer => {
                    return observer.next(
                        params.get('error') === 'true' ? true : false,
                    );
                });
            }),
        );

        this.errorParam.subscribe(result => {
            if (result) {
                this.msgText =
                    'To view the selected page, you must first log into Galaxy by clicking on one of the above SCMs';
            } else {
                this.msgText =
                    'Log into Galaxy by clicking on one of the above SCMs';
            }
        });
    }

    login(): void {
        this.connectingMsg = 'Connecting to the mother ship...';
        window.location.href =
            '/accounts/github/login/?next=' + this.redirectUrl;
    }
}
