import {
	Component,
    Input,
    OnInit,
    AfterViewInit
} from '@angular/core';

import {
    Router
} from '@angular/router';

import { Namespace }    from '../../resources/namespaces/namespace';

@Component({
    selector:    'carousel-component',
    templateUrl: './carousel.component.html',
    styleUrls:   ['./carousel.component.less']
})
export class CarouselComponent implements OnInit {

    @Input()
    set vendors(data: Namespace[]) {
        this._vendors = JSON.parse(JSON.stringify(data));
        this._vendors.forEach(vendor => {
            if (!vendor.avatar_url) {
                vendor.avatar_url = '/assets/avatar.png';
                vendor['displayClass'] = 'missing-avatar';
                vendor['displayName'] = vendor.name;
            } else {
                vendor['displayClass'] = '';
                vendor['displayName'] = '';
            }
        })
    }

    get vendors(): Namespace[] {
        return this._vendors;
    }

    _vendors: Namespace[] = [];

    constructor(
        private router: Router
    ) {}

    ngOnInit() {}

    handleLeftClick() {
        document.getElementById('slider-inner').scrollLeft += 260;
        console.log(document.getElementById('slider-inner').scrollLeft);
    }

    handleRightClick() {
        document.getElementById('slider-inner').scrollLeft -= 260;
        console.log(document.getElementById('slider-inner').scrollLeft);
    }

    handleVendorClick(vendor:Namespace) {
        let params = {
            'vendor': 'true',
            'namespaces': vendor.name
        }
        this.router.navigate(['/', 'search'], {queryParams: params});
    }
}
