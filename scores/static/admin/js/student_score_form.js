(function($) {
    $(document).ready(function() {
        // Function to update subjects based on selected grade
        function updateSubjects() {
            var gradeId = $('#id_grade').val();
            var subjectSelect = $('#id_subject');
            
            // Clear existing options
            subjectSelect.empty();
            
            if (gradeId) {
                // Add loading option
                subjectSelect.append($('<option></option>').val('').text('در حال بارگذاری...'));
                
                // Fetch subjects for the selected grade
                $.get('/admin/scores/subject/get_subjects/', {grade_id: gradeId}, function(data) {
                    subjectSelect.empty();
                    subjectSelect.append($('<option></option>').val('').text('---------'));
                    
                    $.each(data, function(index, subject) {
                        subjectSelect.append($('<option></option>')
                            .val(subject.id)
                            .text(subject.name));
                    });
                });
            } else {
                subjectSelect.append($('<option></option>').val('').text('---------'));
            }
        }

        // Function to update classes based on selected grade
        function updateClasses() {
            var gradeId = $('#id_grade').val();
            var classSelect = $('#id_class');
            
            // Clear existing options
            classSelect.empty();
            
            if (gradeId) {
                // Add loading option
                classSelect.append($('<option></option>').val('').text('در حال بارگذاری...'));
                
                // Fetch classes for the selected grade
                $.get('/admin/scores/class/get_classes/', {grade_id: gradeId}, function(data) {
                    classSelect.empty();
                    classSelect.append($('<option></option>').val('').text('---------'));
                    
                    $.each(data, function(index, class_) {
                        classSelect.append($('<option></option>')
                            .val(class_.id)
                            .text(class_.name));
                    });
                });
            } else {
                classSelect.append($('<option></option>').val('').text('---------'));
            }
        }

        // Function to update students based on selected class
        function updateStudents() {
            var classId = $('#id_class').val();
            var studentSelect = $('#id_student');
            
            // Clear existing options
            studentSelect.empty();
            
            if (classId) {
                // Add loading option
                studentSelect.append($('<option></option>').val('').text('در حال بارگذاری...'));
                
                // Fetch students for the selected class
                $.get('/admin/scores/student/get_students/', {class_id: classId}, function(data) {
                    studentSelect.empty();
                    studentSelect.append($('<option></option>').val('').text('---------'));
                    
                    $.each(data, function(index, student) {
                        studentSelect.append($('<option></option>')
                            .val(student.id)
                            .text(student.full_name));
                    });
                });
            } else {
                studentSelect.append($('<option></option>').val('').text('---------'));
            }
        }

        // Bind change events
        $('#id_grade').change(function() {
            updateSubjects();
            updateClasses();
        });

        $('#id_class').change(function() {
            updateStudents();
        });

        // Initial update if values are already selected
        if ($('#id_grade').val()) {
            updateSubjects();
            updateClasses();
        }
        if ($('#id_class').val()) {
            updateStudents();
        }
    });
})(django.jQuery); 