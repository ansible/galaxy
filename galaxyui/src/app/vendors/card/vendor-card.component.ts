import {
    Component,
    Input,
    OnInit
} from '@angular/core';

import {
    Router
} from '@angular/router';

import { Namespace }     from '../../resources/namespaces/namespace';

@Component({
    selector: 'vendor-card',
    templateUrl: './vendor-card.component.html',
    styleUrls: ['./vendor-card.component.less']
})
export class VendorCardComponent implements OnInit {

    constructor(
        private router: Router
    ) {}

    _vendor: Namespace;

    @Input()
    set vendor(data: Namespace) {
        this._vendor = data;
    }

    get vendor(): Namespace {
        return this._vendor;
    }

    ngOnInit() {
        if (this.vendor) {
            if (!this.vendor.avatar_url) {
                this.vendor['displayName'] = this.vendor.name;
                this.vendor.avatar_url = '/assets/avatar.png';
            } else {
                this.vendor['displayName'] = '';
            }
            this.vendor['contentCount'] = 0;
            if (this.vendor['summary_fields']['content_counts']) {
                for (const key in this.vendor['summary_fields']['content_counts']) {
                    if (this.vendor['summary_fields']['content_counts'].hasOwnProperty(key)) {
                        this.vendor['contentCount'] += this.vendor['summary_fields']['content_counts'][key];
                    }
                }
            }
        }
    }

    handleCardClick() {
        this.router.navigate(['/', this.vendor.name]);
    }
}
