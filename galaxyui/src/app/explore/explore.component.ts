import { Component, OnInit } from '@angular/core';
import { Repository } from '../resources/respositories/repository';
import { RepositoryService } from '../resources/respositories/repository.service';
import { ListConfig }     from 'patternfly-ng/list/basic-list/list-config';


@Component({
  selector: 'app-explore',
  templateUrl: './explore.component.html',
  styleUrls: ['./explore.component.less']
})
export class ExploreComponent implements OnInit {
  headerTitle: string="Explore"
  mostStarred: Repository[] = [];


  constructor(
    private repositoryService: RepositoryService,
  ) { }

  ngOnInit() {
    this.getMostStarred();
  }

  getMostStarred(): void{
    this.repositoryService.query({"order_by": "-stargazers_count", "page_size": "10"})
      .subscribe(repositories => {
        this.mostStarred = repositories;
        console.log(this.mostStarred);
      });
  }

}
