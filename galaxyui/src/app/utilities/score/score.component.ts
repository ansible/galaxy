import { Component, Input, OnInit } from '@angular/core';

interface IRepoScore {
    community_score: any;
    quality_score?: any;
    community_survey_count: number;
}

@Component({
    selector: 'app-score',
    templateUrl: './score.component.html',
    styleUrls: ['./score.component.less'],
})
export class ScoreComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'ScoreComponent';

    constructor() {}

    _repo: IRepoScore;
    @Input()
    set repo(r: any) {
        this._repo = r as IRepoScore;
    }
    get repo() {
        return this._repo;
    }

    score: number;

    scoreClass: string;

    ngOnInit() {
        if (this.repo.quality_score === undefined) {
            this.repo.quality_score = null;
        }
        let survey_count;

        if (this.repo.community_survey_count > 3) {
            survey_count = 3;
        } else {
            survey_count = this.repo.community_survey_count;
        }

        if (
            this.repo.community_score !== null &&
            this.repo.quality_score !== null
        ) {
            this.score =
                this.repo.quality_score * ((6 - survey_count) / 6) +
                this.repo.community_score * (survey_count / 6);
        } else {
            this.score = this.repo.community_score || this.repo.quality_score;
        }

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
