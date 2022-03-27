import React from 'react';
import $ from 'jquery';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';

class KnowledgeCenter extends React.Component {

    constructor(props) {
        super(props);

        this.state = {

        };
    }

    componentDidMount() {
        // Request default data
    }

    render() {


        return (
            <Container fluid>
                <Row>
                    This is the KnowledgeCenter.
                </Row>
            </Container>
        );
    }

}

export default KnowledgeCenter;
