import {
    Component,
    OnInit,
    AfterViewInit
} from '@angular/core';

import {
    ActivatedRoute,
    Router
} from '@angular/router';

import {
    CardConfig
} from 'patternfly-ng/card/basic-card/card-config';

import { Namespace }              from '../resources/namespaces/namespace';

import * as $ from 'jquery';

@Component({
    selector:    'home',
    templateUrl: './home.component.html',
    styleUrls:   ['./home.component.less']
})
export class HomeComponent implements OnInit, AfterViewInit {

    downloadConfig: CardConfig;
    shareConfig: CardConfig;
    featureConfig: CardConfig;

    downloadContent: string;
    shareContent: string;
    featuredBlogContent: string;
    headerTitle = '<i class="fa fa-home"></i> Home';
    searchText = '';
    showCards = false;
    vendors: Namespace[] = [];

    constructor(
        private route: ActivatedRoute,
        private router: Router
    ) {}

    ngOnInit() {
        this.route.data.subscribe((data) => {
            this.vendors = data['vendors']['results'];
            data['contentBlocks'].forEach(item => {
                switch (item.name) {
                    case 'main-downloads':
                        this.downloadContent = item.content;
                        break;
                    case 'main-share':
                        this.shareContent = item.content;
                        break;
                    case 'main-featured-blog':
                        this.featuredBlogContent = item.content;
                        break;
                }
            });
        });

        this.downloadConfig = {
            titleBorder: true
        } as CardConfig;

        this.shareConfig = {
            titleBorder: true
        } as CardConfig;

        this.featureConfig = {
            titleBorder: true
        } as CardConfig;
    }

    onResize($event) {
        this.showCards = false;
        this.setCardHeight();
    }

    ngAfterViewInit() {
        this.setCardHeight();
    }

    searchContent(): void {
        this.router.navigate(['/search'], {queryParams: {keywords: this.searchText}});
    }

    // private

    private setCardHeight(): void {
        // Set the cards to a consistent height
        setTimeout(_ => {
            const windowHeight = window.innerHeight;
            const windowWidth = window.innerWidth;
            $('#card-1 .pfng-card').css('height', 'auto');
            $('#card-2 .pfng-card').css('height', 'auto');
            $('#card-3 .pfng-card').css('height', 'auto');
            const height1 = $('#card-1 .pfng-card').height();
            const height2 = $('#card-2 .pfng-card').height();
            const height3 = $('#card-3 .pfng-card').height();
            const height = Math.max(height1, height2, height3);
            if (windowWidth > 768 && !isNaN(height)) {
                $('#card-1 .pfng-card').css('height', height);
                $('#card-2 .pfng-card').css('height', height);
                $('#card-3 .pfng-card').css('height', height);
            } else {
                $('#card-1 .pfng-card').css('height', 'auto');
                $('#card-2 .pfng-card').css('height', 'auto');
                $('#card-3 .pfng-card').css('height', 'auto');
            }
            this.showCards = true;
        }, 500);
    }
}
