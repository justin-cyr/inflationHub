import React from 'react';

import CloseButton from 'react-bootstrap/CloseButton';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';

class CpiLevelDataPointForm extends React.Component {

    constructor(props) {
        super(props);
    }

    prependSingleDigitWithZero(n) {
        // return '0n' if n < 10, otherwise return n as a string.
        return n < 10 ? '0'.concat(n) : String(n)
    }

    render() {

        return (
            <Container>
                <Row>
                    <Col>
                        <Form.Group
                            as={Row}
                        >
                            <Form.Label column md="auto">Date:</Form.Label>
                            <Col>
                                <Form.Control
                                    type="date"
                                    value={this.props.date || ''}
                                    onChange={(e) => this.props.onDateChange(e.target.value)}
                                    disabled={!this.props.isActive}
                                >
                                </Form.Control>
                            </Col>
                        </Form.Group>
                    </Col>
                    <Col>
                        <Form.Group
                            as={Row}
                        >
                            <Form.Label column md="auto">CPI Level:</Form.Label>
                            <Col>
                                <Form.Control
                                    type="number"
                                    value={this.props.value || ''}
                                    onChange={(e) => this.props.onValueChange(e.target.value)}
                                    disabled={!this.props.isActive}
                                >
                                </Form.Control>
                            </Col>
                        </Form.Group>
                    </Col>
                    <Col md="auto">
                        <Form.Check
                            type="checkbox"
                            checked={this.props.isActive}
                            onChange={() => this.props.onBoxCheck() }
                        />
                    </Col>
                    <Col md="auto">
                        <CloseButton
                            variant="white"
                            onClick={ () => this.props.onCloseButton() }
                        />
                    </Col>
                </Row>
            </Container>
        );
    }

}

export default CpiLevelDataPointForm;
