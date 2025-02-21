from models.model import Model
from tensorflow.keras import Sequential, layers, models
from tensorflow.keras.layers.experimental.preprocessing import Rescaling
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.models import load_model

class TransferedModel(Model):
    def _define_model(self, input_shape, categories_count):
        # Load the pre-trained facial expression model with correct filename
        base_model = load_model('part_six_basic_model.keras')
        
        # Create new sequential model
        self.model = Sequential([
            # Input processing
            layers.Rescaling(1./255, input_shape=input_shape),
            
            # First maxpool to reduce input size
            layers.MaxPooling2D(2),
            
            # Transfer the conv layer
            layers.Conv2D(32, 3, padding='same', activation='relu'),
            
            # Second maxpool
            layers.MaxPooling2D(2)
        ])
        
        # Copy and freeze weights from base model's conv layers
        for i, layer in enumerate(self.model.layers[2:4]):  # Skip rescaling and first maxpool
            layer.set_weights(base_model.layers[i+2].get_weights())
            layer.trainable = False
        
        # Add classification head
        self.model.add(layers.Dropout(0.25))
        self.model.add(layers.Flatten())
        self.model.add(layers.Dense(8, activation='relu'))
        self.model.add(layers.Dropout(0.25))
        self.model.add(layers.Dense(categories_count, activation='softmax'))
    
    def _compile_model(self):
        self.model.compile(
            optimizer=RMSprop(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
