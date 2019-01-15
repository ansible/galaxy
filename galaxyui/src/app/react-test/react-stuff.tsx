import * as React from 'react';
import * as ReactDOM from 'react-dom';

import {
    CardGrid,
    Row,
    Col,
    Card,
    CardTitle,
    CardBody,
    CardFooter,
    CardDropdownButton,
    MenuItem,
    CardLink,
    CardHeading,
    Icon,
} from 'patternfly-react';

class Test extends React.Component<{}, {}> {
    render() {
        return (
            <CardGrid>
                <Row style={{ marginBottom: '20px', marginTop: '20px' }}>
                    <Col xs={12} md={5}>
                        <Card>
                            <CardTitle>Card Title</CardTitle>
                            <CardBody>[card contents]</CardBody>
                            <CardFooter>
                                <CardDropdownButton
                                    id='cardDropdownButton1'
                                    title='Last 30 Days'
                                    // onClick={onClick}
                                >
                                    <MenuItem eventKey='1' active>
                                        Last 30 Days
                                    </MenuItem>
                                    <MenuItem eventKey='2'>
                                        Last 60 Days
                                    </MenuItem>
                                    <MenuItem eventKey='3'>
                                        Last 90 Days
                                    </MenuItem>
                                </CardDropdownButton>
                                <CardLink
                                    disabled
                                    // onClick={handleClick}
                                    icon={<Icon />}
                                >
                                    View CPU Events
                                </CardLink>
                            </CardFooter>
                        </Card>
                    </Col>
                    <Col xs={12} md={5}>
                        <Card>
                            <CardTitle>Card Title</CardTitle>
                            <CardBody>[card contents]</CardBody>
                            <CardFooter>
                                <CardDropdownButton
                                    id='cardDropdownButton1'
                                    title='Last 30 Days'
                                    // onClick={onClick}
                                >
                                    <MenuItem eventKey='1' active>
                                        Last 30 Days
                                    </MenuItem>
                                    <MenuItem eventKey='2'>
                                        Last 60 Days
                                    </MenuItem>
                                    <MenuItem eventKey='3'>
                                        Last 90 Days
                                    </MenuItem>
                                </CardDropdownButton>
                                <CardLink
                                    // onClick={handleClick}
                                    href='#'
                                    icon={<Icon />}
                                >
                                    Add New Cluster
                                </CardLink>
                            </CardFooter>
                        </Card>
                    </Col>
                    <Col xs={12} md={5}>
                        <Card>
                            <CardHeading>
                                <CardDropdownButton
                                    id='cardDropdownButton1'
                                    title='Last 30 Days'
                                    // onClick={onClick}
                                >
                                    <MenuItem eventKey='1' active>
                                        Last 30 Days
                                    </MenuItem>
                                    <MenuItem eventKey='2'>
                                        Last 60 Days
                                    </MenuItem>
                                    <MenuItem eventKey='3'>
                                        Last 90 Days
                                    </MenuItem>
                                </CardDropdownButton>
                                <CardTitle>
                                    <Icon name='shield' />
                                    Card Title
                                </CardTitle>
                            </CardHeading>
                            <CardBody>[card contents]</CardBody>
                        </Card>
                    </Col>
                    <Col xs={12} md={5}>
                        <Card style={{ height: '120px' }}>
                            <CardTitle>Empty Card</CardTitle>
                            <CardBody>[card contents]</CardBody>
                        </Card>
                    </Col>
                </Row>
            </CardGrid>
        );
    }
}

export class TestComponent {
    static init() {
        ReactDOM.render(<Test />, document.getElementById('react-container'));
    }
}
