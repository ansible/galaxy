import { Component, Input, OnInit } from '@angular/core';

@Component({
    selector: 'app-score',
    templateUrl: './score.component.html',
    styleUrls: ['./score.component.less'],
})
export class ScoreComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'ScoreComponent';

    constructor() {}

    @Input()
    score: number;

    scoreClass: string;

    ngOnInit() {
        this.scoreClass = this.getScoreColor(this.score);

        if (this.score !== null) {
            this.score = Math.round(this.score * 10) / 10;
        }
    }

    getScoreColor(score: number) {
        if (score > 3.5) {
            return 'fa-check-circle score-green';
        }

        if (score >= 1) {
            return 'fa-exclamation-circle score-yellow';
        }

        return 'fa-times-circle score-red';
    }
}
