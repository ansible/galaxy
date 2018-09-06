import { Component, Input, OnInit } from '@angular/core';

@Component({
    selector: 'app-score-bar',
    templateUrl: './score-bar.component.html',
    styleUrls: ['./score-bar.component.less'],
})
export class ScoreBarComponent implements OnInit {
    constructor() {}

    @Input()
    score: number;

    @Input()
    text: string;

    @Input()
    dividend = 5;

    @Input()
    extraInfo: string;

    @Input()
    customTextStyle: string;

    ngOnInit() {}

    // Calculates the width of the green rating bar.
    getWidthPercentage(rating: number): string {
        return (rating / 5) * 100 + '%';
    }
}
