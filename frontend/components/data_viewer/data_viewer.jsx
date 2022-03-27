import React from 'react';
import $ from 'jquery';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';

class DataViewer extends React.Component {

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
                    This is the DataViewer.
                </Row>
            </Container>
        );
    }

}

export default DataViewer;

